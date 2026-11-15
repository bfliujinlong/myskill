#!/usr/bin/env bash
# auto-disk-guard.sh — 系统盘空间守护脚本
# 阈值: 系统盘使用率 > 35% 时触发清理
# 安全红线: 绝不删除 hermes-install / OpenMAIC / cloud-docs / hermes-deploy

set -euo pipefail

# ============ 配置 ============
THRESHOLD=35                    # 系统盘使用率阈值 (%)
ROOT_DEV="/"                    # 系统盘挂载点
LOG_FILE="/home/ubuntu/.hermes/logs/auto-disk-guard.log"
LOCK_FILE="/tmp/auto-disk-guard.lock"
VERBOSE=false                   # 设置为 true 可记录每个跳过的文件

# 安全保护目录（绝对禁止删除）
PROTECTED_DIRS=(
  "/data/hermes-install"
  "/data/OpenMAIC"
  "/data/cloud-docs"
  "/data/cloud-docs-local"
  "/data/hermes-deploy"
  "/data/pcs-presales-ps"
  "/data/tenders"
  "/data/crowdsec"
  "/data/unified-monitoring-agent"
  "/data/cache"
  "/data/hermes-lsp"
)

# ============ 函数 ============
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log_console() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

get_usage_pct() {
  df "$ROOT_DEV" | awk 'NR==2 {gsub(/%/,""); print $5}'
}

# 返回 0 = 安全可删, 返回 1 = 受保护不可删
is_safe_to_delete() {
  local target="$1"
  for protected in "${PROTECTED_DIRS[@]}"; do
    if [[ "$target" == "$protected"* ]] || [[ "$target" == "$protected" ]]; then
      return 1  # 受保护
    fi
  done
  return 0  # 安全可删
}

safe_rm() {
  local path="$1"
  
  if ! is_safe_to_delete "$path"; then
    if [[ "$VERBOSE" == "true" ]]; then
      log "SKIP (protected): $path"
    fi
    return 0
  fi
  
  local size_before
  size_before=$(du -sh "$path" 2>/dev/null | awk '{print $1}')
  rm -rf "$path"
  log "CLEANED: $path (freed ~$size_before)"
}

# ============ 主逻辑 ============
main() {
  # 防止并发
  if [[ -f "$LOCK_FILE" ]]; then
    log_console "Another instance is running, exiting."
    exit 0
  fi
  touch "$LOCK_FILE"
  trap 'rm -f "$LOCK_FILE"' EXIT

  local usage
  usage=$(get_usage_pct)
  log_console "=== Disk Guard Check ==="
  log_console "Current / usage: ${usage}% (threshold: ${THRESHOLD}%)"

  if [[ "$usage" -le "$THRESHOLD" ]]; then
    log_console "OK: Usage below threshold. No action needed."
    return 0
  fi

  log_console "ALERT: Usage ${usage}% > ${THRESHOLD}%. Starting cleanup..."

  # ---------- 1. /tmp 旧文件 (>3天, ubuntu拥有) ----------
  log_console "--- Cleaning /tmp (files older than 3 days, ubuntu-owned) ---"
  while IFS= read -r -d '' f; do
    if [[ -f "$f" && "$(stat -c '%U' "$f" 2>/dev/null)" == "ubuntu" ]]; then
      safe_rm "$f" || true
    fi
  done < <(find /tmp -type f -mtime +3 -print0 2>/dev/null)
  # 清理空目录（排除 /tmp 本身）
  find /tmp -mindepth 1 -type d -empty -delete 2>/dev/null || true

  # ---------- 2. uv 缓存 ----------
  log_console "--- Cleaning uv cache ---"
  if command -v uv &>/dev/null; then
    uv cache clean 2>/dev/null || true
    log "uv cache cleaned via uv"
  fi
  # 手动清理 uv 缓存目录
  for uv_path in /home/ubuntu/.cache/uv/archive-v0 /home/ubuntu/.cache/uv/simple-v24 /home/ubuntu/.cache/uv/wheels-v6 /home/ubuntu/.local/share/uv; do
    if [[ -e "$uv_path" ]]; then
      safe_rm "$uv_path"
    fi
  done

  # ---------- 3. pip 缓存 ----------
  log_console "--- Cleaning pip cache ---"
  if command -v pip &>/dev/null; then
    pip cache purge 2>/dev/null || true
    log "pip cache purged"
  fi
  if [[ -d "/home/ubuntu/.cache/pip" ]]; then
    safe_rm "/home/ubuntu/.cache/pip"
  fi

  # ---------- 4. npm/pnpm 缓存 ----------
  log_console "--- Cleaning npm/pnpm cache ---"
  for cache_path in /home/ubuntu/.cache/pnpm /home/ubuntu/.cache/npm /home/ubuntu/.npm; do
    if [[ -e "$cache_path" ]]; then
      safe_rm "$cache_path"
    fi
  done

  # ---------- 5. systemd journal ----------
  log_console "--- Vacuuming systemd journal ---"
  journalctl --vacuum-size=50M 2>/dev/null || true
  journalctl --vacuum-time=7d 2>/dev/null || true

  # ---------- 6. /var/log 旧日志 ----------
  log_console "--- Cleaning old /var/log files ---"
  find /var/log -name "*.gz" -mtime +7 -delete 2>/dev/null || true
  find /var/log -name "*.old" -delete 2>/dev/null || true
  find /var/log -name "*.1" -mtime +3 -delete 2>/dev/null || true

  # ---------- 7. /data/log 旧日志 ----------
  log_console "--- Cleaning old /data/log files ---"
  find /data/log -name "*.gz" -mtime +3 -delete 2>/dev/null || true
  for i in 1 2 3 4 5 6 7; do
    find /data/log -name "*.${i}" -delete 2>/dev/null || true
  done
  # btmp 轮转
  find /data/log -name "btmp.*" -mtime +7 -delete 2>/dev/null || true

  # ---------- 8. Hermes cron 输出 ----------
  log_console "--- Cleaning Hermes cron output ---"
  if [[ -d "/home/ubuntu/.hermes/cron/output" ]]; then
    find /home/ubuntu/.hermes/cron/output -type f -mtime +2 -delete 2>/dev/null || true
  fi
  # 清理旧 lock 文件
  find /home/ubuntu/.hermes/cron -name "*.lock" -mtime +1 -delete 2>/dev/null || true

  # ---------- 9. 旧 snap 版本 ----------
  log_console "--- Cleaning old snap revisions ---"
  snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | while read -r name rev; do
    snap remove "$name" --revision="$rev" 2>/dev/null || true
    log "Removed old snap: $name rev $rev"
  done

  # ---------- 10. apt 缓存 ----------
  log_console "--- Cleaning apt cache ---"
  apt-get autoclean -y 2>/dev/null || true
  apt-get autoremove -y 2>/dev/null || true

  # ---------- 11. 旧备份文件 ----------
  log_console "--- Cleaning old backups ---"
  if [[ -d "/data/backups" ]]; then
    find /data/backups -name "skills_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
  fi

  # ---------- 12. 孤立 pnpm-store ----------
  log_console "--- Checking duplicate pnpm-store ---"
  if [[ -d "/data/pnpm-store" && -d "/data/.pnpm-store" ]]; then
    local_size=$(du -s /data/pnpm-store 2>/dev/null | awk '{print $1}')
    dot_size=$(du -s /data/.pnpm-store 2>/dev/null | awk '{print $1}')
    if [[ "$dot_size" -ge "$local_size" ]]; then
      safe_rm "/data/pnpm-store"
    fi
  fi

  # ---------- 结果 ----------
  local new_usage
  new_usage=$(get_usage_pct)
  log_console "=== Cleanup Complete ==="
  log_console "Before: ${usage}% -> After: ${new_usage}%"
  
  if [[ "$new_usage" -gt "$THRESHOLD" ]]; then
    log_console "WARNING: Still above threshold after cleanup!"
    return 1
  fi
  
  log_console "OK: Usage now below threshold."
  return 0
}

main "$@"
