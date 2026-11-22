#!/bin/bash
# Qwen 路由测试脚本 (直接执行, 非默认模型)
# 分析: Azure gpt-4o (azure-foundry)
# 先确认 .env
source /home/ubuntu/.hermes/hermes-install/venv/bin/activate 2>/dev/null || true
export OCI_CONFIG_DIR=/home/ubuntu/.oci 2>/dev/null || true
# 测试 Qwen dashscope (直接 curl, 不改默认)
curl -s -o /tmp/qwen_route_result.json -w "%{http_code}" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"hello"}]}' \
  https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions
echo "HTTP 状态: $?"
echo "结果文件: /tmp/qwen_route_result.json"
echo "提示: 200=可用; 404=端点/模型不匹配; 401=key无效"
