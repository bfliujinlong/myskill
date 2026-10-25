#!/usr/bin/env python3
"""
model-discovery-sync.py — one-shot helper that:
  1. Runs discover.py (fetches + merges catalog),
  2. Runs probe.py (tests reachability),
  3. Runs report.py (prints summary to stdout).
Used by cron and by hand. Exits non-zero if any stage fails.
"""

import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path.home() / ".hermes" / "skills" / "model-discovery"
DISCOVERY_DIR = Path.home() / ".hermes" / "model-discovery"
VENV_PYTHON = Path("/home/ubuntu/.hermes/hermes-install/venv/bin/python3")


def run(script: str, label: str) -> bool:
    path = SKILL_DIR / "scripts" / script
    if not path.exists():
        print(f"ERROR: {script} not found at {path}", file=sys.stderr)
        return False
    print(f"\n===== {label} =====")
    result = subprocess.run([str(VENV_PYTHON), str(path)], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        # Only print stderr if something went wrong
        if result.returncode != 0:
            print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    ok = True
    ok &= run("discover.py", "Discover platforms")
    ok &= run("probe.py", "Probe reachability")
    ok &= run("report.py", "Summary report")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
