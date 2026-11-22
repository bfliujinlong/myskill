#!/bin/bash
# 每日增量备份交付物到 /data (150G免费盘)
# 备份: skills / memory / oci-monitor配置 (cloud-docs已在/data盘, 不重复同步)
set -e
BAK=/data/backups
TS=$(date +%Y%m%d)
LOG=$BAK/backup.log

mkdir -p "$BAK"

# 打包 skills + memory (每日快照, 保留7天)
tar czf "$BAK/skills_$TS.tar.gz" -C ~ .hermes/skills .hermes/memory 2>>"$LOG" || true
find "$BAK" -name "skills_*.tar.gz" -mtime +7 -delete 2>/dev/null

echo "[$(date -u +%FT%TZ)] 备份完成 skills+memory快照=$(du -sh $BAK 2>/dev/null|cut -f1) 磁盘余量=$(df -h /data|tail -1|awk '{print $4}')" >> "$LOG"
