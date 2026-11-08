#!/usr/bin/env python3
"""Deterministic pricing computation for ms-pricing-support.

所有数字必须来自显式输入参数（config JSON）。任何缺失或非数值的数字
（quantity / unit_price / recurring_months / discount_rate）都会导致非零退出，
且不产出报价表。脚本不引入任何默认价格、汇率或模型推断数字。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REQUIRED_TOP_FIELDS = ("currency", "one_time_items", "recurring_items", "recurring_months", "discount_rate")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_item(item: dict[str, Any], where: str) -> None:
    if not isinstance(item, dict):
        raise ValueError(f"{where}: item must be an object")
    if "item" not in item or not str(item.get("item", "")).strip():
        raise ValueError(f"{where}: missing item name")
    for field in ("quantity", "unit_price"):
        if field not in item:
            raise ValueError(f"{where}: missing explicit number '{field}' for '{item.get('item')}'")
        if not is_number(item[field]):
            raise ValueError(f"{where}: '{field}' for '{item.get('item')}' is not an explicit number")


def validate_config(config: dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_TOP_FIELDS if f not in config]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if not is_number(config["recurring_months"]):
        raise ValueError("recurring_months must be an explicit number")
    if not is_number(config["discount_rate"]):
        raise ValueError("discount_rate must be an explicit number")
    if not (0 <= float(config["discount_rate"]) <= 1):
        raise ValueError("discount_rate must be within [0, 1]")
    if not isinstance(config["one_time_items"], list) or not isinstance(config["recurring_items"], list):
        raise ValueError("one_time_items and recurring_items must be lists")
    for idx, item in enumerate(config["one_time_items"]):
        validate_item(item, f"one_time_items[{idx}]")
    for idx, item in enumerate(config["recurring_items"]):
        validate_item(item, f"recurring_items[{idx}]")


def compute(config: dict[str, Any]) -> dict[str, Any]:
    one_time_total = 0.0
    one_time_lines = []
    for item in config["one_time_items"]:
        line = float(item["quantity"]) * float(item["unit_price"])
        one_time_lines.append({"item": item["item"], "quantity": item["quantity"],
                               "unit": item.get("unit", ""), "unit_price": item["unit_price"],
                               "line_total": round(line, 2)})
        one_time_total += line

    monthly_total = 0.0
    recurring_lines = []
    for item in config["recurring_items"]:
        line = float(item["quantity"]) * float(item["unit_price"])
        recurring_lines.append({"item": item["item"], "quantity": item["quantity"],
                                "unit": item.get("unit", ""), "unit_price": item["unit_price"],
                                "monthly_total": round(line, 2)})
        monthly_total += line

    months = float(config["recurring_months"])
    discount = float(config["discount_rate"])
    recurring_gross = monthly_total * months
    recurring_discount = recurring_gross * discount
    recurring_net = recurring_gross - recurring_discount
    grand_total = one_time_total + recurring_net

    return {
        "currency": config["currency"],
        "one_time_lines": one_time_lines,
        "one_time_total": round(one_time_total, 2),
        "recurring_lines": recurring_lines,
        "monthly_total": round(monthly_total, 2),
        "recurring_months": config["recurring_months"],
        "recurring_gross": round(recurring_gross, 2),
        "discount_rate": discount,
        "recurring_discount": round(recurring_discount, 2),
        "recurring_net": round(recurring_net, 2),
        "grand_total": round(grand_total, 2),
        "source": "所有数字来自显式输入参数，无模型推断。"
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic pricing computation")
    parser.add_argument("--config", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_json(Path(args.config))
        validate_config(config)
        result = compute(config)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
