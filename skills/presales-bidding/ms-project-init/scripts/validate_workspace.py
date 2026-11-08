#!/usr/bin/env python3
"""Read-only validator for ms-project-init Workspaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from init_workspace import inspect_workspace


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a PCS presales Workspace")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--engagement-type", choices=(
        "managed-service",
        "build-implementation",
        "consulting-assessment",
        "hybrid-integration",
    ))
    parser.add_argument("--company-kb-path", default="_shared/company-knowledge")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = inspect_workspace(Path(args.workspace), args.engagement_type, args.company_kb_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["missing"] or report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
