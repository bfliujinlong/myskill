#!/usr/bin/env python3
"""资源评估聚合计算：覆盖率、分域汇总、缺口清单。

用法:
    python3 aggregate.py inventory.json

输入 JSON:
    {
      "expected":  [{"id": "vm-001", "domain": "compute"}, ...],
      "collected": [{"id": "vm-001", "domain": "compute", "spec": "8C16G"}, ...],
      "unmatched": [{"id": "vm-007", "reason": "只读账号无该地域权限"}, ...]
    }

输出: 结构化 JSON 到 stdout（coverage / by_domain / missing_ids / gaps / passed）
退出码: 0 = 覆盖率达标；1 = 存在缺口需升级；2 = 输入不可用
"""
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"文件不存在: {src}", file=sys.stderr)
        return 2

    data = json.loads(src.read_text(encoding="utf-8"))
    expected = data.get("expected", [])
    collected = data.get("collected", [])
    unmatched = data.get("unmatched", [])

    if not expected:
        print("expected 为空，无法计算覆盖率", file=sys.stderr)
        return 2

    expected_ids = {item["id"] for item in expected if "id" in item}
    collected_ids = {item["id"] for item in collected if "id" in item}

    missing = sorted(expected_ids - collected_ids)
    rate = len(expected_ids & collected_ids) / len(expected_ids) if expected_ids else 0.0

    # 分域汇总
    by_domain: dict[str, dict[str, int]] = {}
    for item in expected:
        d = item.get("domain", "unknown")
        by_domain.setdefault(d, {"expected": 0, "collected": 0})["expected"] += 1
    for item in collected:
        d = item.get("domain", "unknown")
        by_domain.setdefault(d, {"expected": 0, "collected": 0})["collected"] += 1

    result = {
        "skill": "mig-resource-assessment",
        "check": "coverage",
        "source": str(src),
        "coverage": {
            "expected": len(expected_ids),
            "collected": len(expected_ids & collected_ids),
            "rate": round(rate, 4),
            "missing": len(missing),
        },
        "by_domain": by_domain,
        "missing_ids": missing,
        "gaps": unmatched,
        "passed": not missing,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    pct = f"{rate * 100:.1f}%"
    print(f"覆盖率 {pct}（{len(expected_ids & collected_ids)}/{len(expected_ids)}）",
          file=sys.stderr)
    if missing:
        print(f"❌ 缺口 {len(missing)} 项，需进升级包: {', '.join(missing[:10])}",
              file=sys.stderr)
        return 1
    print("✅ 清单全量采集到，无缺口", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
