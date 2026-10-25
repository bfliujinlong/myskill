#!/usr/bin/env python3
"""
model-discovery-report.py — Generate a human-readable summary report from
catalog.json + probes.json + user config.

Output: Markdown report printed to stdout (or written to --output FILE).

The report is sorted with EU-accessible / reachable platforms first so the
French/ Paris user sees the best options at the top.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_DIR = Path.home() / ".hermes"
DISCOVERY_DIR = HERMES_DIR / "model-discovery"
CATALOG_FILE = DISCOVERY_DIR / "catalog.json"
PROBES_FILE = DISCOVERY_DIR / "probes.json"


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def eu_sort_key(p: dict) -> tuple:
    """Sort key: reachable first, then EU-accessible, then name."""
    probes = p.get("_probes", [])
    reachable = any(pr.get("reachable") for pr in probes) if probes else None
    eu = p.get("eu_accessible")
    name = p.get("name", "").lower()
    # Higher priority first ( False > None > True  is NOT what we want;
    # we want reachable True first, EU True first)
    r_rank = 0 if reachable else (1 if reachable is False else 2)
    eu_rank = 0 if eu else (1 if eu is False else 2)
    return (r_rank, eu_rank, name)


def build_report() -> str:
    catalog = load_json(CATALOG_FILE)
    probes_raw = load_json(PROBES_FILE)

    if catalog is None or "platforms" not in catalog:
        return "ERROR: No catalog found. Run discover.py first."

    platforms = catalog["platforms"]
    probe_map: dict[str, list] = {}
    if probes_raw and isinstance(probes_raw, dict) and "results" in probes_raw:
        for r in probes_raw["results"]:
            probe_map[r.get("platform", "").lower()] = [r]

    # Attach probe data to each platform
    for p in platforms:
        name_lower = p["name"].lower()
        p["_probes"] = probe_map.get(name_lower, [])

    platforms_sorted = sorted(platforms, key=eu_sort_key)

    lines: list[str] = []
    lines.append("# Free LLM API Platforms — Accessibility Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    total = len(platforms_sorted)
    reachable = sum(1 for p in platforms_sorted if any(pr.get("reachable") for pr in p.get("_probes", [])))
    eu_ok = sum(1 for p in platforms_sorted if p.get("eu_accessible"))
    lines.append(f"- Total platforms catalogued: **{total}**")
    lines.append(f"- Confirmed reachable from this host: **{reachable}**")
    lines.append(f"- EU-hosted or EU-accessible: **{eu_ok}**")
    lines.append(f"- Require API key (per catalog metadata): **{sum(1 for p in platforms_sorted if p.get('needs_api_key'))}**")
    lines.append(f"- User-added custom entries: **{sum(1 for p in platforms_sorted if p.get('custom'))}**")
    lines.append("")

    lines.append("## Platform Details")
    lines.append("")
    for p in platforms_sorted:
        name = p.get("name", "?")
        base_url = p.get("base_url", "")
        desc = p.get("description", "")
        models = p.get("models", [])
        needs_key = p.get("needs_api_key")
        eu = p.get("eu_accessible")
        country = p.get("country", "")
        flag = p.get("flag", "")
        url = p.get("url", "")
        custom = p.get("custom", False)
        rate_note = p.get("rate_limit_note", "")

        probes = p.get("_probes", [])
        reachable = any(pr.get("reachable") for pr in probes)
        probe_latency = next((pr.get("latency_ms") for pr in probes if pr.get("reachable")), None)
        probe_auth = next((pr.get("auth_required") for pr in probes if pr.get("reachable")), None)
        probe_error = next((pr.get("probes", [{}])[0].get("error") for pr in probes if not pr.get("reachable")), None)

        lines.append(f"### {flag} {name}")
        lines.append("")
        lines.append(f"- **Country/Region:** {country or 'n/a'}")
        lines.append(f"- **EU accessible (metadata):** {'Yes' if eu else ('No' if eu is False else 'Unknown')}")
        lines.append(f"- **Reachable from this host:** {'✅ Yes' if reachable else '❌ No'}")
        if reachable:
            lines.append(f"- **Observed latency:** {probe_latency} ms")
            lines.append(f"- **Auth required (observed):** {'Yes' if probe_auth else 'No'}")
        else:
            if probe_error:
                lines.append(f"- **Probe error:** `{probe_error[:120]}`")
        lines.append(f"- **Needs API key (metadata):** {'Yes' if needs_key else 'No'}")
        lines.append(f"- **Rate limit note:** {rate_note or 'n/a'}")
        lines.append(f"- **API docs/keys:** [{url or 'n/a'}]({url or '#'})" if url else "- **API docs/keys:** n/a")
        lines.append(f"- **Base URL:** `{base_url or 'n/a'}`")
        if desc:
            lines.append(f"- **Description:** {desc}")
        if models:
            lines.append(f"- **Known models ({len(models)}):** `{', '.join(models[:8])}`{' +more' if len(models) > 8 else ''}")
        if custom:
            lines.append("- **⚠️ User-added custom entry**")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("_Report generated by Hermes model-discovery skill. Refresh with `/cron daily discover`._")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate free LLM API accessibility report")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Write report to file instead of stdout")
    args = parser.parse_args()

    report = build_report()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
        return 0
    else:
        print(report)
        return 0


if __name__ == "__main__":
    sys.exit(main())
