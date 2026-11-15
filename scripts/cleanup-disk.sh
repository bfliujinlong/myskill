#!/bin/bash
# cleanup-disk.sh - 定期清理磁盘空间(目标: 30G 小盘不爆)
# 清理对象(安全, 不碰业务数据/配置/记忆):
#   - apt 缓存
#   - pip/npm 缓存
#   - Hermes deploy 下的第三方 clone (dsh-src/dsh-npm, 可重新拉)
#   - 旧的日志/临时
# 绝不清理: config.yaml / memories/ / skills/ / credentials/ / auth.json
set -e

echo "[$(date)] 开始磁盘清理"

# 1. apt 缓存
sudo apt-get clean 2>/dev/null || apt-get clean 2>/dev/null || true
echo "apt clean done"

# 2. npm 缓存 (可重建)
npm cache clean --force 2>/dev/null || true
echo "npm cache cleaned"

# 3. pip 缓存
rm -rf ~/.cache/pip 2>/dev/null || true
echo "pip cache cleaned"

# 4. Hermes deploy 下第三方 clone (dsh 源码, 占 1.5G, 可重新 git clone)
rm -rf ~/.hermes/deploy/dsh-src ~/.hermes/deploy/dsh-npm 2>/dev/null || true
echo "deploy third-party cleaned"

# 5. 旧日志(保留最近)
find ~/.hermes/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
echo "old logs cleaned"

# 6. 系统 journal
sudo journalctl --vacuum-time=7d 2>/dev/null || journalctl --vacuum-time=7d 2>/dev/null || true

echo "[$(date)] 清理完成"
df -h / | tail -1
