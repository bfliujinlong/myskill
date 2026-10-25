#!/usr/bin/env bash
# model-discovery-daily.sh — cron wrapper: discover → probe → report
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISCOVERY_DIR="$HOME/.hermes/model-discovery"
VENV_PYTHON="${HERMES_VENV_PYTHON:-/home/ubuntu/.hermes/hermes-install/venv/bin/python3}"

log() { echo "[$(date -u +%FT%TZ)] $*"; }

log "=== model-discovery daily run ==="

log "discover..."
"$VENV_PYTHON" "$SCRIPT_DIR/discover.py" || log "DISCOVER FAILED"

log "probe..."
"$VENV_PYTHON" "$SCRIPT_DIR/probe.py" || log "PROBE FAILED"

REPORT_FILE="$DISCOVERY_DIR/report-$(date -u +%Y%m%d).md"
log "report → $REPORT_FILE"
"$VENV_PYTHON" "$SCRIPT_DIR/report.py" -o "$REPORT_FILE" || log "REPORT FAILED"

log "done."
