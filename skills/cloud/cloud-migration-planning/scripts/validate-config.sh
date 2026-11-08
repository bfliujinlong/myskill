#!/bin/bash
# validate-config.sh - Validate infrastructure configuration
# Usage: ./validate-config.sh <config_file>

set -euo pipefail

CONFIG_FILE="${1:?Usage: $0 <config_file>}"

echo "Validating: $CONFIG_FILE"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: file not found: $CONFIG_FILE"
  exit 1
fi

if [ ! -s "$CONFIG_FILE" ]; then
  echo "ERROR: file is empty: $CONFIG_FILE"
  exit 1
fi

# 语法 + 必填字段校验
if /home/ubuntu/.hermes/hermes-install/venv/bin/python3 -c "import yaml" 2>/dev/null; then
  /home/ubuntu/.hermes/hermes-install/venv/bin/python3 - "$CONFIG_FILE" <<'PY'
import sys, yaml
p = sys.argv[1]
try:
    d = yaml.safe_load(open(p, encoding='utf-8'))
except yaml.YAMLError as e:
    print("ERROR: YAML syntax invalid:", str(e).splitlines()[0])
    sys.exit(1)
if not isinstance(d, dict):
    print("ERROR: top level must be a mapping")
    sys.exit(1)
print("  [OK] YAML syntax valid, top-level keys:", len(d))

required = ["environment", "region"]
missing = [k for k in required if k not in d]
for k in missing:
    print(f"  [MISSING] required field: {k}")

raw = open(p, encoding='utf-8').read()
todo = sum(1 for line in raw.splitlines() if "TODO" in line)
if todo:
    print(f"  [WARN] {todo} TODO placeholder(s) not customized")

if missing:
    print("Validation FAILED: missing required fields")
    sys.exit(1)
print("Validation PASSED")
PY
  exit $?
else
  echo "  [WARN] PyYAML unavailable, degraded mode"
  echo "Validation complete (degraded mode)."
fi
