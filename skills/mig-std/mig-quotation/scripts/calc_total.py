#!/usr/bin/env python3
"""报价总额测算：角色 × 人天 × 单价 = 小计，各行小计之和 = 总计。

用法:
    python3 calc_total.py wbs.json
    python3 calc_total.py wbs.json --rate 350
    python3 calc_total.py wbs.json --out total.json

输入 JSON:
    {
      "rate": 350,
      "rows": [
        {"role": "架构师", "days": 15},
        {"role": "迁移工程师", "days": 120, "rate": 380}
      ]
    }
  - rate 可在顶层统一给定，也可每行覆盖（按角色议价）
  - days 支持小数（如 0.5）

退出码: 0 = 成功；2 = 输入不可用
输出: 结构化 JSON 到 stdout（进 WBS 与报价单），人类可读表格到 stderr
"""
import argparse
import json
import sys
from pathlib import Path

DEFAULT_RATE = 350


def fail(msg: str) -> int:
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.stderr.write(f"[calc_total] 失败: {msg}\n")
    return 2


def load_rows(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在: {path}")
    if path.suffix.lower() != ".json":
        raise ValueError(f"不支持的输入格式: {path.suffix}（仅支持 .json）")
    # json 解析失败必须显式暴露，不让 traceback 逃逸
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"输入顶层必须是对象: {type(data).__name__}")
    rows = data.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"rows 必须是列表: {type(rows).__name__}")
    rate = data.get("rate", DEFAULT_RATE)
    if rate is not None and not isinstance(rate, (int, float)):
        raise ValueError(f"rate 必须是数字或 null: {type(rate).__name__}")
    if rate is None:
        rate = DEFAULT_RATE
    return rate, rows


def _num(v, field, i):
    """转数字并拒绝 NaN/Infinity；类型不符抛 TypeError，由调用方统一捕获。"""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise TypeError(f"第 {i} 行 {field} 必须是数字，实为 {type(v).__name__}")
    f = float(v)
    if f != f or f in (float("inf"), float("-inf")):
        raise ValueError(f"第 {i} 行 {field} 不得为 NaN/Infinity")
    return f


def calc(rows, default_rate):
    out_rows = []
    total = 0.0
    total_days = 0.0
    for i, r in enumerate(rows, 1):
        if not isinstance(r, dict):
            raise TypeError(f"第 {i} 行必须是对象，实为 {type(r).__name__}")
        try:
            role = r["role"]
        except KeyError:
            raise ValueError(f"第 {i} 行缺少 role: {r}")
        if not isinstance(role, str) or not role.strip():
            raise TypeError(f"第 {i} 行 role 必须是非空字符串，实为 {type(role).__name__}")
        days = _num(r["days"], "days", i) if "days" in r else None
        if days is None:
            raise ValueError(f"第 {i} 行缺少 days: {r}")
        rate = _num(r["rate"], "rate", i) if r.get("rate") is not None else _num(default_rate, "rate", i)
        if days < 0 or rate < 0:
            raise ValueError(f"第 {i} 行 days/rate 不得为负: {r}")
        subtotal = round(days * rate, 2)
        total += subtotal
        total_days += days
        out_rows.append({
            "role": role,
            "days": days,
            "rate": rate,
            "subtotal": subtotal,
        })
    return out_rows, round(total_days, 2), round(total, 2)


def main() -> int:
    ap = argparse.ArgumentParser(description="报价总额测算")
    ap.add_argument("wbs", help="WBS JSON 路径")
    ap.add_argument("--rate", type=float, default=None, help="覆盖单价基准（默认按输入文件或 350）")
    ap.add_argument("--out", default=None, help="结果 JSON 落盘路径")
    args = ap.parse_args()

    try:
        file_rate, rows = load_rows(Path(args.wbs))
    except Exception as e:  # 输入不可用必须显式暴露，不吞异常
        return fail(str(e))

    if not isinstance(rows, list):
        return fail(f"rows 必须是列表: {type(rows).__name__}")
    if not rows:
        return fail("rows 为空，无法测算")

    rate = args.rate if args.rate is not None else file_rate
    try:
        out_rows, total_days, total = calc(rows, rate)
    except (TypeError, ValueError) as e:  # 输入非法必须显式暴露，不吞异常
        return fail(str(e))

    result = {
        "ok": True,
        "rate": rate,
        "rows": out_rows,
        "total_days": total_days,
        "total": total,
        "note": "金额单位与 rate 一致（默认 USD）",
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        try:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        except OSError as e:  # 落盘失败必须显式暴露，不吞异常
            return fail(f"写入 {args.out} 失败: {e}")
        sys.stderr.write(f"[calc_total] 已写入 {args.out}\n")
    print(text)

    sys.stderr.write(f"{'角色':<14}{'人天':>8}{'单价':>10}{'小计':>14}\n")
    for r in out_rows:
        sys.stderr.write(f"{r['role']:<14}{r['days']:>8.2f}{r['rate']:>10.2f}{r['subtotal']:>14,.2f}\n")
    sys.stderr.write(f"{'总计':<14}{total_days:>8.2f}{'':>10}{total:>14,.2f}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
