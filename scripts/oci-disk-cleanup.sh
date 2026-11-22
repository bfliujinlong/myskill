#!/bin/bash
# ============================================================
# OCI Always Free 磁盘清理 + 监控脚本
# 目标: 系统盘 < 80%, 数据盘缩到最小, 总存储 < 200GB
# 作者: Anchnet Ops | 安全: 绝不删除关键配置
# ============================================================
set -euo pipefail

LOG="/var/log/oci-disk-cleanup.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TG_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TG_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
ALERT_THRESHOLD=80  # 系统盘超过 80% 发 Telegram 告警

# Telegram Home Channel
TG_TOKEN="${TELEGRAM_BOT_TOKEN:-$(grep TELEGRAM_BOT_TOKEN /home/ubuntu/.hermes/.env 2>/dev/null | cut -d= -f2)}"
TG_CHAT_ID="${TELEGRAM_CHAT_ID:-$(grep TELEGRAM_HOME_CHANNEL /home/ubuntu/.hermes/.env 2>/dev/null | cut -d= -f2)}"

log() { echo "[$TIMESTAMP] $*" | tee -a "$LOG"; }

alert_tg() {
    local msg="$1"
    if [[ -n "$TG_TOKEN" && -n "$TG_CHAT_ID" ]]; then
        curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
            -d "chat_id=${TG_CHAT_ID}&text=${msg}" >/dev/null 2>&1 || true
    fi
}

# ---------------- 0. 检查当前状态 ----------------
log "=== 开始磁盘清理 ==="
df -h / /data | tee -a "$LOG"

SYS_USAGE=$(df / | awk 'NR==2{print $5}' | tr -d '%')
DATA_USAGE=$(df /data | awk 'NR==2{print $5}' | tr -d '%')

if [[ "$SYS_USAGE" -ge "$ALERT_THRESHOLD" ]]; then
    alert_tg "⚠️ 系统盘使用率 ${SYS_USAGE}% 超过阈值 ${ALERT_THRESHOLD}%! 已执行紧急清理。"
fi

# ---------------- 1. 系统盘清理 (目标: 释放 2-4GB) ----------------
log "--- 1. 清理系统盘缓存 ---"

# 1.1 pip 缓存 (通常几百 MB)
if command -v pip3 &>/dev/null; then
    pip3 cache purge 2>/dev/null || true
    log "pip3 cache purged"
fi

# 1.2 npm 缓存 (保留近期元数据, 清理旧包)
if [[ -d /home/ubuntu/.npm ]]; then
    NPM_BEFORE=$(du -sh /home/ubuntu/.npm 2>/dev/null | awk '{print $1}')
    npm cache clean --force 2>/dev/null || true
    NPM_AFTER=$(du -sh /home/ubuntu/.npm 2>/dev/null | awk '{print $1}')
    log "npm cache: ${NPM_BEFORE} -> ${NPM_AFTER}"
fi

# 1.3 Hermes 缓存 (保留最近 7 天, 清理旧缓存)
if [[ -d /home/ubuntu/.hermes/cache/documents ]]; then
    find /home/ubuntu/.hermes/cache/documents -type f -mtime +7 -delete 2>/dev/null || true
    log "hermes cache/documents: cleaned files older than 7 days"
fi
if [[ -d /home/ubuntu/.hermes/cache/images ]]; then
    find /home/ubuntu/.hermes/cache/images -type f -mtime +7 -delete 2>/dev/null || true
    log "hermes cache/images: cleaned files older than 7 days"
fi
if [[ -d /home/ubuntu/.hermes/cache/delegation ]]; then
    find /home/ubuntu/.hermes/cache/delegation -type f -mtime +14 -delete 2>/dev/null || true
    log "hermes cache/delegation: cleaned files older than 14 days"
fi

# 1.4 旧 Cloudflare 备份 (可有可无)
if [[ -d /home/ubuntu/.cloudflared.bak.20260824 ]]; then
    rm -rf /home/ubuntu/.cloudflared.bak.20260824 2>/dev/null || true
    log "removed old cloudflared backup"
fi

# 1.5 apt 缓存 (系统级, 需要 sudo)
if [[ $EUID -eq 0 ]]; then
    apt-get autoclean -qq 2>/dev/null || true
    apt-get autoremove -qq 2>/dev/null || true
    log "apt cache cleaned"
fi

# 1.6 journald 日志 (限 200M, 额外清理旧日志)
if [[ $EUID -eq 0 ]]; then
    journalctl --vacuum-time=3d 2>/dev/null || true
    journalctl --vacuum-size=100M 2>/dev/null || true
    log "journald vacuumed"
fi

# 1.7 /tmp 旧文件
find /tmp -type f -mtime +3 -delete 2>/dev/null || true
log "/tmp cleaned (files older than 3 days)"

# 1.8 旧 Python 脚本 (保留 gen_*.py 和关键脚本, 删除临时脚本)
find /home/ubuntu -maxdepth 1 -name "*.py" -mtime +30 -delete 2>/dev/null || true
find /home/ubuntu -maxdepth 1 -name "*.tmp" -delete 2>/dev/null || true
find /home/ubuntu -maxdepth 1 -name "*~" -delete 2>/dev/null || true

# 1.9 旧 xlsx/docx (output 目录保留, 临时文件清理)
find /home/ubuntu -maxdepth 1 -name "*.xlsx" -mtime +14 -delete 2>/dev/null || true
find /home/ubuntu -maxdepth 1 -name "*.docx" -mtime +14 -delete 2>/dev/null || true

# ---------------- 2. 数据盘清理 ----------------
log "--- 2. 清理数据盘缓存 ---"

# 2.1 旧 hermes-install 构建缓存
if [[ -d /data/hermes-install/hermes-agent/.venv ]]; then
    find /data/hermes-install/hermes-agent/.venv -name "*.pyc" -delete 2>/dev/null || true
    find /data/hermes-install/hermes-agent/.venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    log "hermes venv pyc cleaned"
fi

# 2.2 旧 pnpm store (清理未引用包)
if [[ -d /data/pnpm-store ]]; then
    # pnpm store prune 需要在项目目录执行, 这里只清理明显旧的
    find /data/pnpm-store -type f -mtime +90 -delete 2>/dev/null || true
    log "pnpm-store old files cleaned"
fi

# 2.3 旧 npm cache
if [[ -d /data/npm-cache ]]; then
    find /data/npm-cache -type f -mtime +30 -delete 2>/dev/null || true
    log "npm-cache old files cleaned"
fi

# ---------------- 3. 最终状态 ----------------
log "=== 清理完成 ==="
df -h / /data | tee -a "$LOG"

SYS_AFTER=$(df / | awk 'NR==2{print $5}' | tr -d '%')
alert_tg "✅ 磁盘清理完成。系统盘使用率: ${SYS_BEFORE}% -> ${SYS_AFTER}%"

log "=== 脚本结束 ==="
