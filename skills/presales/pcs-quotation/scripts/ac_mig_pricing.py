#!/usr/bin/env python3
"""AC-MIG 定价确定性计算（见 ../references/ac-mig-pricing.md）。

用途：当 MCP tool 不可达，或 llm_used=false 需要人工能快速核对汇总金额时，
不依赖 LLM，纯算术得出 total_person_days / total_amount，与 SKILL.md 描述的
"风险溢价在汇总后统一乘"规则保持一致。

用法:
    python3 ac_mig_pricing.py '<workstreams_json>' [risk_premium]

    workstreams_json 形如:
    [
      {"workstream": "Landing Zone", "role": "云架构师", "person_days": 5, "daily_rate": 3500},
      {"workstream": "数据迁移", "role": "DBA", "person_days": 8, "daily_rate": 3000}
    ]

纯 stdlib，无第三方依赖。
"""
from __future__ import annotations

import json
import sys
from typing import Any

REQUIRED_WORKSTREAMS = ["Landing Zone", "迁移设计", "数据迁移", "应用迁移", "切割切换", "运维交接"]


def compute_quotation(line_items: list[dict[str, Any]], risk_premium: float = 1.1) -> dict[str, Any]:
    """按 AC-MIG 方法论汇总报价。

    line_items 每条需含 workstream/role/person_days/daily_rate。
    返回结构对齐 Generate-Quotation 的 output_schema：
    workstreams / total_person_days / total_amount / currency / notes。
    """
    by_workstream: dict[str, list[dict[str, Any]]] = {}
    total_person_days = 0.0
    raw_subtotal = 0.0

    for item in line_items:
        ws = item["workstream"]
        pd = float(item["person_days"])
        rate = float(item["daily_rate"])
        subtotal = round(pd * rate, 2)
        by_workstream.setdefault(ws, []).append({
            "role": item["role"],
            "person_days": pd,
            "daily_rate": rate,
            "subtotal": subtotal,
        })
        total_person_days += pd
        raw_subtotal += subtotal

    total_amount = round(raw_subtotal * risk_premium, 2)

    covered = set(by_workstream.keys())
    missing = [w for w in REQUIRED_WORKSTREAMS if w not in covered]
    notes = []
    if missing:
        notes.append(f"以下 Workstream 本次报价为 0 人天（未出现在输入中）: {', '.join(missing)}")
    notes.append(f"风险溢价系数 {risk_premium} 已在汇总后统一乘，非逐条乘。")

    return {
        "workstreams": [
            {"name": ws, "lines": lines, "subtotal": round(sum(l["subtotal"] for l in lines), 2)}
            for ws, lines in by_workstream.items()
        ],
        "total_person_days": round(total_person_days, 2),
        "total_amount": total_amount,
        "currency": "CNY",
        "notes": notes,
    }


def _self_check() -> None:
    """单元自检：给定样例数据，核对汇总金额是否符合手算结果。"""
    sample = [
        {"workstream": "Landing Zone", "role": "云架构师", "person_days": 5, "daily_rate": 3500},
        {"workstream": "数据迁移", "role": "DBA", "person_days": 8, "daily_rate": 3000},
        {"workstream": "应用迁移", "role": "迁移工程师", "person_days": 10, "daily_rate": 2500},
    ]
    # 手算: 5*3500=17500; 8*3000=24000; 10*2500=25000; raw=66500; *1.1=73150
    result = compute_quotation(sample, risk_premium=1.1)
    assert result["total_person_days"] == 23.0, result
    assert result["total_amount"] == 73150.0, result
    assert "Landing Zone" in [w["name"] for w in result["workstreams"]]
    missing_note = next(n for n in result["notes"] if n.startswith("以下"))
    for w in ["迁移设计", "切割切换", "运维交接"]:
        assert w in missing_note
    print("self-check OK:", json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _self_check()
    else:
        items = json.loads(sys.argv[1])
        premium = float(sys.argv[2]) if len(sys.argv) > 2 else 1.1
        print(json.dumps(compute_quotation(items, premium), ensure_ascii=False, indent=2))
