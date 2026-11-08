#!/usr/bin/env python3
"""校验报价测算：人天 × 单价 = 小计，各行小计之和 = 总计。

用法:
    python3 validate_quote.py quote.json      # 校验 JSON
    python3 validate_quote.py quote.xlsx      # 校验 Excel（列: 角色/人天/单价/小计）

退出码: 0 = 通过；1 = 校验失败；2 = 输入不可用
输出: 结构化 JSON 到 stdout，人类可读摘要到 stderr
"""
import json
import sys
from pathlib import Path

DEFAULT_RATE = 350


def load_rows(path: Path):
    """从 JSON 或 XLSX 载入 (角色, 人天, 单价, 声明小计) 行。"""
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        rate = data.get("unit_price", DEFAULT_RATE)
        rows = []
        for item in data.get("wbs", []) + data.get("risk_days", []):
            rows.append((
                item.get("role", ""),
                float(item.get("days", 0)),
                float(item.get("unit_price", rate)),
                float(item.get("subtotal", 0)) if "subtotal" in item else None,
            ))
        declared_total = data.get("total_amount")
        return rows, declared_total

    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            from openpyxl import load_workbook
        except ImportError:
            print("缺少 openpyxl，无法读取 xlsx", file=sys.stderr)
            sys.exit(2)
        ws = load_workbook(path, data_only=True).active
        rows = []
        for r in ws.iter_rows(min_row=2, values_only=True):
            if not r or r[0] is None:
                continue
            # 期望列: 角色 | 工作内容 | 人天 | 单价 | 小计
            role = str(r[0])
            days = float(r[2]) if len(r) > 2 and r[2] is not None else 0
            rate = float(r[3]) if len(r) > 3 and r[3] is not None else DEFAULT_RATE
            sub = float(r[4]) if len(r) > 4 and r[4] is not None else None
            rows.append((role, days, rate, sub))
        return rows, None

    print(f"不支持的文件类型: {path.suffix}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2

    rows, declared_total = load_rows(src)
    if not rows:
        print(f"未读到任何测算行: {src}", file=sys.stderr)
        return 2

    errors = []
    total_days = 0.0
    total_amount = 0.0
    for role, days, rate, declared_sub in rows:
        expect_sub = days * rate
        total_days += days
        total_amount += expect_sub
        if declared_sub is not None and abs(declared_sub - expect_sub) > 0.01:
            errors.append({
                "type": "row_subtotal_mismatch",
                "role": role,
                "declared": declared_sub,
                "expected": expect_sub,
            })

    if declared_total is not None and abs(declared_total - total_amount) > 0.01:
        errors.append({
            "type": "total_mismatch",
            "declared": declared_total,
            "expected": total_amount,
        })

    result = {
        "skill": "mig-quotation",
        "check": "quote_validation",
        "source": str(src),
        "row_count": len(rows),
        "total_days": round(total_days, 2),
        "total_amount": round(total_amount, 2),
        "errors": errors,
        "passed": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print(f"行数 {len(rows)} ｜ 总人天 {total_days:g} ｜ 总金额 {total_amount:,.0f}",
          file=sys.stderr)
    if errors:
        print(f"❌ 校验失败 {len(errors)} 处", file=sys.stderr)
        return 1
    print("✅ 校验通过：人天×单价=小计，小计之和=总计", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
