#!/usr/bin/env python3
"""Deterministic Workspace initializer for ms-project-init."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE_ROOT / "references" / "workspace-schema.json"
DIRECTORY_TEMPLATE_PATH = PACKAGE_ROOT / "templates" / "directory-README.md"
ROOT_TEMPLATE_PATH = PACKAGE_ROOT / "templates" / "root-README.md"
INIT_REPORT_TEMPLATE_PATH = PACKAGE_ROOT / "templates" / "init-report.md"
REQUIRED_FIELDS = (
    "project_id",
    "customer_name",
    "opportunity_name",
    "opportunity_type",
    "engagement_type",
    "stage",
    "owner",
    "selected_offerings",
    "language",
    "sensitivity",
)
ALLOWED_ENGAGEMENT_TYPES = {
    "managed-service",
    "build-implementation",
    "consulting-assessment",
    "hybrid-integration",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_config(config: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in config or config[field] in (None, "", [])]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if config["engagement_type"] not in ALLOWED_ENGAGEMENT_TYPES:
        raise ValueError(f"unsupported engagement_type: {config['engagement_type']}")
    if not isinstance(config["selected_offerings"], list):
        raise ValueError("selected_offerings must be a list")


def safe_target(workspace: Path, relative: str) -> Path:
    target = (workspace / relative).resolve()
    root = workspace.resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"path escapes workspace: {relative}")
    return target


def render_directory_readme(item: dict[str, str], schema: dict[str, Any]) -> str:
    rules = schema["common_rules"]
    template = DIRECTORY_TEMPLATE_PATH.read_text(encoding="utf-8")
    values = dict(item)
    values.update(rules)
    return template.format(**values)


def yaml_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def render_project_yaml(config: dict[str, Any]) -> str:
    industry = config.get("industry") or "unconfirmed"
    offerings = "\n".join(f"  - {yaml_string(item)}" for item in config["selected_offerings"])
    return (
        f"schema_version: \"0.1.0\"\n"
        f"project_id: {yaml_string(config['project_id'])}\n"
        f"customer_name: {yaml_string(config['customer_name'])}\n"
        f"opportunity_name: {yaml_string(config['opportunity_name'])}\n"
        f"opportunity_type: {yaml_string(config['opportunity_type'])}\n"
        f"engagement_type: {yaml_string(config['engagement_type'])}\n"
        f"stage: {yaml_string(config['stage'])}\n"
        f"owner: {yaml_string(config['owner'])}\n"
        f"industry: {yaml_string(industry)}\n"
        f"language: {yaml_string(config['language'])}\n"
        f"sensitivity: {yaml_string(config['sensitivity'])}\n"
        f"artifact_status: \"working\"\n"
        f"selected_offerings:\n{offerings}\n"
    )


def render_root_readme(config: dict[str, Any]) -> str:
    template = ROOT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.format(**config)


def render_init_report(config: dict[str, Any]) -> str:
    template = INIT_REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return template.format(**config)


def create_missing(path: Path, content: str, report: dict[str, list[str]]) -> None:
    if path.exists() or path.is_symlink():
        report["skipped"].append(str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    report["created"].append(str(path))


def initialize_workspace(workspace: Path, config: dict[str, Any]) -> dict[str, list[str]]:
    schema = load_json(SCHEMA_PATH)
    report: dict[str, list[str]] = {"created": [], "skipped": [], "warnings": [], "errors": []}
    workspace.mkdir(parents=True, exist_ok=True)
    create_missing(workspace / "README.md", render_root_readme(config), report)
    create_missing(workspace / "project.yaml", render_project_yaml(config), report)
    for item in schema["base_directories"]:
        directory = safe_target(workspace, item["path"])
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            report["created"].append(str(directory))
        create_missing(directory / "README.md", render_directory_readme(item, schema), report)
    module_base = "03_方案与应答/01_服务方案/02_项目类型模块"
    module = schema["engagement_modules"][config["engagement_type"]]
    for item in module["directories"]:
        directory = safe_target(workspace, f"{module_base}/{item['path']}")
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            report["created"].append(str(directory))
        create_missing(directory / "README.md", render_directory_readme(item, schema), report)
    init_report = workspace / "00_项目管理" / "04_项目状态与版本" / "初始化报告.md"
    create_missing(init_report, render_init_report(config), report)
    return report


def read_project_field(project_yaml: Path, field: str) -> str | None:
    if not project_yaml.is_file():
        return None
    prefix = f"{field}:"
    for line in project_yaml.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            raw = line[len(prefix):].strip()
            try:
                return str(json.loads(raw))
            except json.JSONDecodeError:
                return raw.strip('"')
    return None


def expected_readmes(workspace: Path, engagement_type: str) -> list[Path]:
    schema = load_json(SCHEMA_PATH)
    paths = [safe_target(workspace, item["path"]) / "README.md" for item in schema["base_directories"]]
    module_base = "03_方案与应答/01_服务方案/02_项目类型模块"
    module = schema["engagement_modules"].get(engagement_type)
    if module:
        paths.extend(safe_target(workspace, f"{module_base}/{item['path']}") / "README.md" for item in module["directories"])
    return paths


def inspect_workspace(workspace: Path, engagement_type: str | None, company_kb_path: str) -> dict[str, list[str]]:
    report: dict[str, list[str]] = {"missing": [], "warnings": [], "errors": []}
    if not workspace.is_dir():
        report["errors"].append(f"workspace not found: {workspace}")
        return report
    for root_file in (workspace / "README.md", workspace / "project.yaml"):
        if not root_file.is_file():
            report["missing"].append(str(root_file))
    if not engagement_type:
        engagement_type = read_project_field(workspace / "project.yaml", "engagement_type")
    if engagement_type not in ALLOWED_ENGAGEMENT_TYPES:
        report["errors"].append("valid engagement_type not found")
    else:
        try:
            for readme in expected_readmes(workspace, engagement_type):
                if not readme.is_file():
                    report["missing"].append(str(readme))
        except (ValueError, KeyError, OSError) as exc:
            report["errors"].append(str(exc))
    company_kb = workspace / company_kb_path
    if not company_kb.exists():
        report["warnings"].append(f"Company KB mount missing: {company_kb_path}")
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a PCS presales Workspace")
    parser.add_argument("--mode", choices=("init", "inspect", "repair"), default="init")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--config")
    parser.add_argument("--company-kb-path", default="_shared/company-knowledge")
    return parser.parse_args(argv)


def error_report(message: str) -> dict[str, list[str]]:
    return {"created": [], "skipped": [], "warnings": [], "errors": [message]}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "inspect":
        report = inspect_workspace(Path(args.workspace), None, args.company_kb_path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["missing"] or report["errors"] else 0
    try:
        if not args.config:
            raise ValueError("--config is required for init and repair")
        config = load_json(Path(args.config))
        validate_config(config)
        report = initialize_workspace(Path(args.workspace), config)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps(error_report(str(exc)), ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
