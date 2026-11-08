#!/usr/bin/env python3
"""Knodo adapter: platform-neutral Company KB path resolution.

This lives in the ADAPTER layer, not in any core Skill. Core Skills stay
platform-neutral and never hardcode a Knodo mount path (e.g. `pcs-presales`)
or read platform env vars. The adapter is the single place that injects the
Company KB path into a Skill invocation.

Resolution order (explicit injection only):
  1. explicit --company-kb-path argument;
  2. PCS_COMPANY_KB_PATH environment variable;
  3. none  -> WARN (skeleton work allowed) / BLOCK (before using KB-backed
     capability, pricing, SLA or contract knowledge).

Hard rules:
  - No directory scanning of the Workspace;
  - No guessing a path from directory names;
  - No touch/write probing of a read-only mount (existence check is a
     read-only stat, never a write);
  - Never fabricate a default business path.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ENV_VAR = "PCS_COMPANY_KB_PATH"


def resolve_company_kb_path(explicit: str | None, env: dict | None = None) -> dict:
    """Return a resolution result. Read-only: never writes or touches the mount.

    Result dict:
      {source: "argument"|"env"|"none", path: str|None,
       level: "OK"|"WARN"|"BLOCK", message: str, exists: bool|None}
    """
    env = os.environ if env is None else env
    path: str | None = None
    source = "none"
    if explicit not in (None, ""):
        path, source = explicit, "argument"
    elif env.get(ENV_VAR):
        path, source = env[ENV_VAR], "env"

    if path is None:
        return {
            "source": "none", "path": None, "exists": None, "level": "WARN",
            "message": (
                "Company KB path not injected. Provide --company-kb-path or set "
                f"{ENV_VAR}. Skeleton work may continue (WARN); BLOCK before using "
                "KB-backed capability, pricing, SLA or contract knowledge. "
                "Adapter will NOT scan the Workspace or guess a directory."
            ),
        }

    # Read-only existence check (stat only). No write/touch probing.
    p = Path(path)
    exists = p.exists()
    if not exists:
        return {"source": source, "path": path, "exists": False, "level": "WARN",
                "message": f"Company KB path injected ({source}) but not present: {path}. Not creating it."}
    return {"source": source, "path": path, "exists": True, "level": "OK",
            "message": f"Company KB path resolved from {source}: {path}"}


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Resolve Company KB path (Knodo adapter)")
    ap.add_argument("--company-kb-path", default=None)
    ap.add_argument("--require", action="store_true",
                    help="treat missing injection as BLOCK (exit 3) instead of WARN")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    result = resolve_company_kb_path(args.company_kb_path)
    if args.require and result["source"] == "none":
        result = {**result, "level": "BLOCK",
                  "message": "BLOCK: " + result["message"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["level"] == "BLOCK":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
