#!/usr/bin/env python3
"""校验报价测算：人天 × 单价 = 小计，各行小计之和 × 风险溢价 = 总计。

用法:
    python3 validate_pricing.py quote.json              # 校验 JSON
    python3 validate_pricing.py quote.xlsx              # 校验 Excel（自动定位明细表）
    python3 validate_pricing.py quote.xlsx --sheet 表2   # 指定工作表
    python3 validate_pricing.py quote.json 1.1          # 指定风险溢价系数（默认 1.1）

支持的 JSON 结构（自动识别，无需指定）:
    A) AC-MIG 输出（ac_mig_pricing.py / pcs-quotation）:
       {"workstreams":[{"name":..,"lines":[{"role","person_days","daily_rate","subtotal"}]}],
        "total_person_days":..,"total_amount":..}
    B) 扁平明细（quote_lines.json）:
       [{"workstream","role","person_days","daily_rate"}, ...]
    C) 旧 WBS 结构（mig-quotation templates）:
       {"unit_price":..,"wbs":[{"role","days","unit_price","subtotal"}],
        "risk_days":[...],"total_amount":..}

xlsx 约定：按表头名定位「人天 / 单价 / 小计」列，允许千分位逗号与货币符号。
若活动表不是明细表，自动在所有 sheet 中找含「人天」表头的那张。

退出码: 0 = 通过；1 = 校验失败；2 = 输入不可用
输出: 结构化 JSON 到 stdout，人类可读摘要到 stderr
"""
import json
import re
import sys
from pathlib import Path

DEFAULT_RATE = 350
DEFAULT_PREMIUM = 1.1
EPS = 0.01

DAYS_KEYS = ("person_days", "days", "人天")
RATE_KEYS = ("daily_rate", "unit_price", "单价")


def parse_number(value):
    """把 '3,500' / '¥3,500.00' / 3500 解析成 float；不可解析返回 None。"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"[¥$,，\s]", "", text)
    text = text.replace("**", "")
    if not re.fullmatch(r"[-+]?\d+(\.\d+)?", text):
        return None
    return float(text)


def _to_row(item: dict, default_rate: float):
    """从单条明细取出 (角色, 人天, 单价, 声明小计)。"""
    def pick(keys, fallback):
        for k in keys:
            if item.get(k) is not None:
                num = parse_number(item[k])
                if num is not None:
                    return num
        return fallback

    role = item.get("role") or item.get("name") or ""
    days = pick(DAYS_KEYS, 0.0)
    rate = pick(RATE_KEYS, default_rate)
    declared = parse_number(item.get("subtotal")) if item.get("subtotal") is not None else None
    return (role, days, rate, declared)


def _iter_json_rows(data, default_rate):
    """按 A/B/C 三种结构抽取明细行。"""
    rows = []
    if isinstance(data, list):
        return [_to_row(i, default_rate) for i in data if isinstance(i, dict)]
    if not isinstance(data, dict):
        return None

    for ws in data.get("workstreams", []):
        for line in ws.get("lines", []):
            rows.append(_to_row(line, default_rate))
    for item in data.get("wbs", []) + data.get("risk_days", []):
        rows.append(_to_row(item, default_rate))
    return rows


def _detect_premium(data, rows, declared_total):
    """溢价系数：优先显式声明，否则从总额/明细小计之和反推。"""
    for key in ("risk_premium", "premium"):
        if data.get(key) is not None:
            return float(data[key])
    if declared_total is not None and rows:
        raw = sum(d * r for _, d, r, _ in rows)
        if raw > 0:
            ratio = float(declared_total) / raw
            if abs(ratio - round(ratio, 2)) < 0.005 and 1.0 <= ratio <= 2.0:
                return round(ratio, 2)
    return DEFAULT_PREMIUM


def load_json(path: Path):
    # 坏 JSON / 读不到文件不得抛 traceback，按约定返回退出码 2（输入不可用）
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"JSON 无法解析: {path} -> {exc}", file=sys.stderr)
        sys.exit(2)
    default_rate = DEFAULT_RATE
    if isinstance(data, dict):
        default_rate = parse_number(
            data.get("unit_price") or data.get("daily_rate")) or DEFAULT_RATE
    rows = _iter_json_rows(data, default_rate)
    if rows is None:
        print("JSON 顶层既不是对象也不是数组，无法解析", file=sys.stderr)
        sys.exit(2)
    declared_total = data.get("total_amount") if isinstance(data, dict) else None
    premium = _detect_premium(data, rows, declared_total) if isinstance(data, dict) \
        else DEFAULT_PREMIUM
    return rows, declared_total, premium


def _find_header(rows):
    """在表格前 5 行里找表头行，返回 (行号, 列索引映射)。"""
    for idx, row in enumerate(rows[:5]):
        cells = [str(c).strip().replace("**", "") if c is not None else "" for c in row]
        cols = {}
        for i, cell in enumerate(cells):
            if "人天" in cell and "单价" not in cell:
                cols.setdefault("days", i)
            elif "单价" in cell:
                cols.setdefault("rate", i)
            elif cell == "小计" or "小计" in cell:
                cols.setdefault("subtotal", i)
            elif cell == "角色":
                cols.setdefault("role", i)
        if "days" in cols:
            return idx, cols
    return None, {}


def load_xlsx(path: Path, sheet_name=None):
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("缺少 openpyxl，无法读取 xlsx", file=sys.stderr)
        sys.exit(2)

    wb = load_workbook(path, data_only=True)
    candidates = [wb[sheet_name]] if sheet_name else list(wb.worksheets)

    for ws in candidates:
        grid = [list(r) for r in ws.iter_rows(values_only=True)]
        header_idx, cols = _find_header(grid)
        if header_idx is None:
            continue
        rows = []
        for r in grid[header_idx + 1:]:
            if not r or r[cols["days"]] is None:
                continue
            days = parse_number(r[cols["days"]])
            if days is None:
                continue
            rate = parse_number(r[cols.get("rate", cols["days"])]) if "rate" in cols \
                else None
            if rate is None:
                rate = DEFAULT_RATE
            sub = parse_number(r[cols["subtotal"]]) if "subtotal" in cols else None
            role = str(r[cols["role"]]) if "role" in cols else str(r[0])
            rows.append((role, days, rate, sub))
        if rows:
            return rows, None, DEFAULT_PREMIUM, ws.title

    print(f"xlsx 中未找到含「人天」表头的明细表: {path}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sheet_name = None
    for i, a in enumerate(sys.argv[1:]):
        if a == "--sheet" and i + 1 < len(sys.argv):
            sheet_name = sys.argv[i + 2]

    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    src = Path(args[0])
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2

    sheet_used = None
    if src.suffix.lower() == ".json":
        rows, declared_total, premium = load_json(src)
    elif src.suffix.lower() in (".xlsx", ".xlsm"):
        rows, declared_total, premium, sheet_used = load_xlsx(src, sheet_name)
    else:
        print(f"不支持的文件类型: {src.suffix}", file=sys.stderr)
        return 2

    if len(args) >= 2:
        premium = float(args[1])

    if not rows:
        print(f"未读到任何测算行: {src}", file=sys.stderr)
        return 2

    # 全 0 人天 = 输入不对（列定位失败），不得判为通过
    if all(d == 0 for _, d, _, _ in rows):
        print("所有行人天均为 0，疑似列定位错误，拒绝出校验结论", file=sys.stderr)
        return 2

    errors = []
    total_days = 0.0
    raw_subtotal = 0.0
    for role, days, rate, declared_sub in rows:
        expect_sub = days * rate
        total_days += days
        raw_subtotal += expect_sub
        if declared_sub is not None and abs(declared_sub - expect_sub) > EPS:
            errors.append({
                "type": "row_subtotal_mismatch",
                "role": role,
                "declared": declared_sub,
                "expected": round(expect_sub, 2),
            })

    total_amount = round(raw_subtotal * premium, 2)
    if declared_total is not None and abs(float(declared_total) - total_amount) > EPS:
        errors.append({
            "type": "total_mismatch",
            "declared": float(declared_total),
            "expected": total_amount,
            "raw_subtotal": round(raw_subtotal, 2),
            "risk_premium": premium,
        })

    result = {
        "skill": "mig-quotation",
        "check": "quote_validation",
        "source": str(src),
        "row_count": len(rows),
        "total_days": round(total_days, 2),
        "raw_subtotal": round(raw_subtotal, 2),
        "risk_premium": premium,
        "total_amount": total_amount,
        "errors": errors,
        "passed": not errors,
    }
    if sheet_used:
        result["sheet"] = sheet_used
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"行数 {len(rows)} ｜ 总人天 {total_days:g} ｜ 基准 {raw_subtotal:,.0f} "
          f"｜ 溢价 ×{premium} ｜ 总额 {total_amount:,.0f}", file=sys.stderr)
    if errors:
        print(f"❌ 校验失败 {len(errors)} 处", file=sys.stderr)
        return 1
    print("✅ 校验通过：人天×单价=小计，小计之和×溢价=总计", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
