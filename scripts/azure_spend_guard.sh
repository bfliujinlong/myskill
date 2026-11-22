#!/bin/bash
# Azure Spend Guard - 监控Azure GPT-5-mini用量，防止超支
# 每5分钟运行，触发阈值$50

set -o pipefail

LOG_FILE="$HOME/.hermes/logs/azure_spend.log"
THRESHOLD=50
TELEGRAM_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_HOME_CHANNEL:-5701842056}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 从本地账单文件计算用量
get_azure_usage() {
    local billing_file="$HOME/.hermes/logs/azure_billing.json"
    
    if [ -f "$billing_file" ]; then
        # 读取JSON计费记录
        total=$(python3 -c "
import json
try:
    with open('$billing_file', 'r') as f:
        data = json.load(f)
        print(sum(item.get('cost', 0) for item in data.get('usage', [])))
except:
    print(0)
" 2>/dev/null || echo "0")
        echo "$total"
    else
        echo "0"
    fi
}

# 记录用量（在delegate后调用）
record_usage() {
    local reasoning_tokens=$1
    local timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    
    # GPT-5-mini计费估算：约$0.005/1K tokens
    local cost=$(python3 -c "print(round($reasoning_tokens / 1000 * 0.005, 4))")
    
    python3 - <<EOF
import json, os
billing_file = "$HOME/.hermes/logs/azure_billing.json"
entry = {
    "timestamp": "$timestamp",
    "reasoning_tokens": $reasoning_tokens,
    "model": "gpt-5-mini",
    "cost": $cost
}
try:
    with open(billing_file, 'r') as f:
        data = json.load(f)
except:
    data = {"usage": []}

data["usage"].append(entry)
with open(billing_file, 'w') as f:
    json.dump(data, f, indent=2)
EOF
    
    log "记录用量: $reasoning_tokens tokens, 约 $${cost}"
}

# 发送Telegram告警
send_alert() {
    local message=$1
    
    if [ -n "$TELEGRAM_TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=⚠️ Azure用量告警: ${message}" > /dev/null 2>&1
        log "已发送Telegram告警: $message"
    else
        log "无Telegram token，告警: $message"
    fi
}

# 主逻辑
main() {
    current_usage=$(get_azure_usage)
    log "当前Azure用量: $${current_usage}"
    
    if (( $(echo "$current_usage > $THRESHOLD" | bc -l) )); then
        send_alert "累计用量$${current_usage} 超过阈值$${THRESHOLD}"
        exit 1
    fi
    
    log "Azure用量正常"
}

# 如果有参数，表示是record用法
if [ $# -gt 0 ]; then
    record_usage "$1"
else
    main
fi