#!/bin/bash
# Quick model probe test
set -euo pipefail

ENV="/home/ubuntu/.hermes/.env"
CONFIG="/home/ubuntu/.hermes/config.yaml"

# Read keys
OR_KEY=$(grep -oP 'OPENROUTER_API_KEY=\K.*' "$ENV" 2>/dev/null | tr -d '"' | head -n1 || true)
NOUS_KEY=$(grep -oP 'NOUS_API_KEY=\K.*' "$ENV" 2>/dev/null | tr -d '"' | head -n1 || true)

echo "OR_KEY: [REDACTED]"
echo "NOUS_KEY: [REDACTED]"

# Test one Nous model
if [ -n "${NOUS_KEY:-}" ]; then
    http_code=$(curl -s --max-time 8 -w "%{http_code}" -o /tmp/test_output.txt \
        -H "Authorization: Bearer <REDACTED:API_KEY>" \
        -H "Content-Type: application/json" \
        -d '{"model":"meituan/longcat-2.0:free","messages":[{"role":"user","content":"hi"}],"max_tokens":8}' \
        "https://inference-api.nousresearch.com/v1/chat/completions" 2>/dev/null || echo "000")
    echo "Nous model HTTP code: $http_code"
    cat /tmp/test_output.txt | head -5
else
    echo "Skipping Nous probe (no key)"
fi

# Test one OpenRouter model
if [ -n "${OR_KEY:-}" ]; then
    http_code=$(curl -s --max-time 8 -w "%{http_code}" -o /tmp/test_output2.txt \
        -H "Authorization: Bearer <REDACTED:OPENROUTER_KEY>" \
        -H "Content-Type: application/json" \
        -d '{"model":"nvidia/nemotron-3.5-lightning:free","messages":[{"role":"user","content":"hi"}],"max_tokens":8}' \
        "https://openrouter.ai/api/v1/chat/completions" 2>/dev/null || echo "000")
    echo "OR model HTTP code: $http_code"
    cat /tmp/test_output2.txt | head -5
else
    echo "Skipping OR probe (no key)"
fi

echo "Done"