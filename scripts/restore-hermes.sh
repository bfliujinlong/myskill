#!/bin/bash
# 一键恢复 Hermes + 全套配置 (换机器用)
# 前置: 已 clone hermes-backup 到 ~/.hermes, 且放了 gh-token.txt / dsh credentials / oci config
set -e
HERMES_HOME="/home/ubuntu/.hermes"
BACKUP="$HERMES_HOME/deploy"

echo "[1/6] 恢复 systemd 服务"
sudo cp "$BACKUP/systemd/"*.service /etc/systemd/system/ 2>/dev/null
sudo systemctl daemon-reload

echo "[2/6] 恢复 nginx"
sudo cp "$BACKUP/nginx/dsh-combined" /etc/nginx/sites-enabled/ 2>/dev/null
sudo nginx -t 2>&1 | tail -1

echo "[3/6] 恢复 dsh settings"
mkdir -p ~/.dsh
cp "$BACKUP/dsh/settings.yaml" ~/.dsh/ 2>/dev/null

echo "[4/6] 恢复 oci-monitor 脚本"
cp "$BACKUP/oci-monitor/"*.sh ~/oci-monitor/ 2>/dev/null || { mkdir -p ~/oci-monitor && cp "$BACKUP/oci-monitor/"*.sh ~/oci-monitor/; }
chmod +x ~/oci-monitor/*.sh

echo "[5/6] 恢复 cron"
crontab "$BACKUP/cron/crontab.txt" 2>/dev/null && echo "  cron 已恢复" || echo "  ⚠️ 手动: crontab $BACKUP/cron/crontab.txt"

echo "[6/6] 启动服务"
sudo systemctl enable dsh cloudflared-dsh cloudflared-upload upload-server oci-boot-report 2>/dev/null
sudo systemctl restart dsh nginx 2>/dev/null || true

echo "=== 完成 ==="
echo "需手动补的密钥(不进备份):"
echo "  1. ~/.dsh/.credentials.yaml (dsh token)"
echo "  2. ~/.oci/config (OCI 密钥)"
echo "  3. ~/.hermes/credentials/gh-token.txt (已放则忽略)"
echo "  4. /etc/nginx 若需 HTTPS 证书"
