#!/bin/bash
# OpenRouter / 免費模型可連通性診斷
set -euo pipefail

ENV=/home/ubuntu/.hermes/.env
CONFIG=/home/ubuntu/.hermes/config.yaml
LOG=/tmp/or-diag-$(date +%Y%m%d-%H%M%S).log

OR_KEY=$(grep -oP 'OPENROUTER_API_KEY=\K.*' "$ENV" | tr -d "'\"")

echo "=== OpenRouter 模型可用性診斷 ===" | tee "$LOG"
echo "時間: $(date)" | tee -a "$LOG"
echo "OR_KEY: ${OR_KEY:0:10}...(長度${#OR_KEY})" | tee -a "$LOG"
echo "" | tee -a "$LOG"

# 1. 基礎 API 呼叫測試
echo "=== 1. 基礎 API 測試 ===" | tee -a "$LOG"
curl -s -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}s\n" \
  -H "Authorization: Bearer $OR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax/minimax-m3:free","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
  "https://openrouter.ai/api/v1/chat/completions" 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "=== 2. 關鍵模型測試 (依序，帶詳細錯誤) ===" | tee -a "$LOG"

MODELS=(
  "minimax/minimax-m3:free"
  "minimax/minimax-m2.7:free"
  "nvidia/nemotron-3.5-lightning:free"
  "cohere/north-mini-code:free"
  "google/gemma-4-31b-it:free"
  "tencent/hy3:free"
  "meta-llama/llama-4-scout:free"
  "openai/gpt-4o-mini:free"
)

FAIL_COUNT=0
SUCCESS_COUNT=0

for MODEL in "${MODELS[@]}"; do
  echo -n "[$MODEL] " | tee -a "$LOG"
  HTTP_CODE=$(curl -s -o /tmp/test_${MODEL//\//_}.json -w "%{http_code}" \
    -H "Authorization: Bearer $OR_KEY" \
    -H "Content-Type: application/json" \
    -H "HTTP-Referer: https://hermes.local" \
    -H "X-Title: Hermes" \
    -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}" \
    --max-time 15 \
    "https://openrouter.ai/api/v1/chat/completions" 2>&1)
  
  if [ "$HTTP_CODE" = "200" ]; then
    BODY=$(cat /tmp/test_${MODEL//\//_}.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d,ensure_ascii=False)[:150])" 2>/dev/null)
    echo "HTTP 200 ✓ | $BODY" | tee -a "$LOG"
    SUCCESS_COUNT=$((SUCCESS_COUNT+1))
  else
    echo "HTTP $HTTP_CODE ✗" | tee -a "$LOG"
    cat /tmp/test_${MODEL//\//_}.json 2>/dev/null | head -5 | tee -a "$LOG"
    FAIL_COUNT=$((FAIL_COUNT+1))
  fi
  echo "" | tee -a "$LOG"
done

echo "=== 結果 ===" | tee -a "$LOG"
echo "成功: $SUCCESS_COUNT" | tee -a "$LOG"
echo "失敗: $FAIL_COUNT" | tee -a "$LOG"
echo "日誌: $LOG" | tee -a "$LOG"

# 3. 檢查 config.yaml 當前設定
echo "" | tee -a "$LOG"
echo "=== 3. 當前 config.yaml 設定 ===" | tee -a "$LOG"
echo "default: $(grep 'default:' $CONFIG | head -1 | awk '{print $2}')" | tee -a "$LOG"
echo "provider: $(grep 'provider:' $CONFIG | head -1 | awk '{print $2}')" | tee -a "$LOG"
echo "base_url: $(grep 'base_url:' $CONFIG | head -1 | awk '{print $2}')" | tee -a "$LOG"

# 4. 檢查 cron 狀態
echo "" | tee -a "$LOG"
echo "=== 4. cron 狀態 ===" | tee -a "$LOG"
crontab -l 2>/dev/null | grep -E "hourly-model-guard|daily_global" || echo "無 crontab 項" | tee -a "$LOG"
ls -la /home/ubuntu/.hermes/cron/jobs.json 2>/dev/null && echo "jobs.json 存在" | tee -a "$LOG" || echo "jobs.json 不存在" | tee -a "$LOG"
