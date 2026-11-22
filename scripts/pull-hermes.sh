#!/bin/bash
# 一键拉起 Hermes 环境 (换机器用)
# 用法: bash pull-hermes.sh <github_token>
#   token 需有 bfliujinlong/hermes-backup 的 read 权限(classic token 或 fine-grained repo read)
set -e
TOKEN="${1:-$GITHUB_TOKEN}"
[ -z "$TOKEN" ] && { echo "用法: bash pull-hermes.sh <github_token>"; exit 1; }

HERMES_HOME="/home/ubuntu/.hermes"
REPO="bfliujinlong/hermes-backup"
echo "[1/4] 安装依赖"
sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip git curl jq 2>&1 | tail -1

echo "[2/4] 克隆备份"
rm -rf "$HERMES_HOME"
git clone "https://$TOKEN@github.com/$REPO.git" "$HERMES_HOME" 2>&1 | tail -2

echo "[3/4] 放 token (你手动填 gh-token.txt 才 sync 得动)"
mkdir -p "$HERMES_HOME/credentials"
chmod 700 "$HERMES_HOME/credentials"
echo "  请手动: echo '<token>' > $HERMES_HOME/credentials/gh-token.txt && chmod 600 该文件"

echo "[4/4] 恢复完成"
echo "  skills: $(ls $HERMES_HOME/skills 2>/dev/null | wc -l) 个"
echo "  memory: $(ls $HERMES_HOME/memories/*.md 2>/dev/null | wc -l) 个"
echo "  下一步: 启动 hermes (hermes run) 或 systemd"
