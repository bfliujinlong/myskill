#!/bin/bash
# 启动 litellm 网关 (Codex/CC/Cursor 的 OpenAI 兼容免费路由)
cd ~/.hermes
source /home/ubuntu/.hermes/.env 2>/dev/null
source /home/ubuntu/.litellm-venv/bin/activate
exec litellm --config /home/ubuntu/.hermes/deploy/litellm_config.yaml --port 4100 --host 127.0.0.1
