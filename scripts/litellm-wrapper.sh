#!/bin/bash
# LiteLLM wrapper - sources .env for API keys
set -a
source /home/ubuntu/.hermes/.env
set +a

# Export all API keys for litellm config.yaml os.environ/ references
export LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-sk-litellm-local-master-$(hostname)}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY}"
export AIMLAPI_API_KEY="${AIMLAPI_API_KEY}"
export NOUS_API_KEY="${NOUS_API_KEY}"
export AZURE_FOUNDRY_API_KEY="${AZURE_FOUNDRY_API_KEY}"
export AZURE_API_KEY="${AZURE_API_KEY}"
export AZURE_API_BASE="${AZURE_API_BASE}"
export AZURE_API_VERSION="${AZURE_API_VERSION}"

exec /home/ubuntu/.hermes/hermes-install/venv/bin/litellm --config /home/ubuntu/.litellm/config.yaml
