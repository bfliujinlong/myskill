#!/bin/bash
# setup-mcp-filesystem.sh - 幂等追加 filesystem MCP 配置并重启网关
set -e

CONFIG="/home/bfyalong/.hermes/config.yaml"
PATCH="/home/bfyalong/.hermes/cache/mcp-patch.yaml"
MARK="mcp_servers:"

# 1. 幂等检查：已存在 mcp_servers 则跳过追加
if grep -q "^mcp_servers:" "$CONFIG"; then
  echo "[$(date)] mcp_servers 已存在，跳过追加"
else
  echo "[$(date)] 追加 filesystem MCP 配置..."
  cat "$PATCH" >> "$CONFIG"
  echo "已追加"
fi

# 2. 校验 YAML 仍可解析
python3 -c "import yaml,sys; yaml.safe_load(open('$CONFIG')); print('config.yaml 解析 OK')" \
  || { echo "ERROR: config.yaml 解析失败，请检查"; exit 1; }

# 3. 重启网关（优先 systemd，否则 hermes gateway restart）
if systemctl is-active --quiet hermes-gateway 2>/dev/null; then
  echo "[$(date)] 通过 systemctl 重启网关..."
  sudo systemctl restart hermes-gateway
elif command -v hermes >/dev/null 2>&1; then
  echo "[$(date)] 通过 hermes gateway restart 重启..."
  hermes gateway restart 2>&1 | tail -3 || true
else
  echo "WARN: 未找到重启方式，请手动重启网关"
fi

# 4. 等待片刻后验证 MCP 加载
sleep 5
if command -v hermes >/dev/null 2>&1; then
  echo "[$(date)] 验证 MCP 列表:"
  hermes mcp list 2>&1 | tail -10 || echo "(mcp list 暂不可用，稍后手动验证)"
fi

echo "[$(date)] 任务2完成"
