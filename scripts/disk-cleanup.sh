#!/bin/bash
# 每日磁盘清理脚本 - 控制本地空间
# 运行: cron 每天 09:00 上海时间

set -e

LOG="/tmp/disk-cleanup.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始清理" > "$LOG"

# 记录清理前
BEFORE=$(df -h / | awk 'NR==2 {print $5}')
echo "清理前磁盘使用: $BEFORE" >> "$LOG"

# 1. journald 日志限制 100M
journalctl --vacuum-size=100M >> "$LOG" 2>&1 || true

# 2. apt 缓存
apt clean >> "$LOG" 2>&1 || true
apt autoremove -y >> "$LOG" 2>&1 || true

# 3. npm 缓存
rm -rf ~/.npm/_cacache >> "$LOG" 2>&1 || true

# 4. pip 缓存
rm -rf ~/.cache/pip >> "$LOG" 2>&1 || true

# 5. Hermes 缓存（保留最近7天）
find ~/.hermes/cache -type f -mtime +7 -delete >> "$LOG" 2>&1 || true

# 6. /tmp 旧文件（保留7天）
find /tmp -type f -mtime +7 -delete >> "$LOG" 2>&1 || true

# 7. snap 旧版本
snap list --all | awk '/disabled/{print $1, $3}' | while read name rev; do
  snap remove "$name" --revision="$rev" >> "$LOG" 2>&1 || true
done

# 8. Docker（如有）
if command -v docker &>/dev/null; then
  docker system prune -f >> "$LOG" 2>&1 || true
fi

# 记录清理后
AFTER=$(df -h / | awk 'NR==2 {print $5}')
echo "清理后磁盘使用: $AFTER" >> "$LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理完成" >> "$LOG"

cat "$LOG"
