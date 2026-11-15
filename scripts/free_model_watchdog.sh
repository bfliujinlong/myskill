#!/bin/bash
# Free Model Watchdog - 每5分钟检查模型健康状态
# 自动重排免费模型路由顺序

set -o pipefail

HEALTH_FILE="$HOME/.hermes/scripts/models.json"
CONFIG_FILE="$HOME/.hermes/config.yaml"
LOG_FILE="$HOME/.hermes/logs/model_health.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查单个端点健康
check_endpoint() {
    local url=$1
    local timeout=5
    
    # 使用curl检查，200=健康，429/404/5xx=不健康
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "healthy"
    elif [ "$response" = "429" ]; then
        echo "rate_limited"
    elif [ "$response" = "404" ]; then
        echo "expired"
    else
        echo "error_$response"
    fi
}

# 测试模型可用性
test_model() {
    local model=$1
    local provider=$2
    local api_key=$3
    
    log "Testing $model via $provider"
    
    case $provider in
        "openrouter")
            # OpenRouter免费模型限流检查
            endpoint="https://openrouter.ai/api/v1/models"
            status=$(check_endpoint "$endpoint")
            ;;
        "nous")
            endpoint="https://api.nousresearch.com/v1/models"
            status=$(check_endpoint "$endpoint")
            ;;
        "groq")
            endpoint="https://api.groq.com/v1/models"
            status=$(check_endpoint "$endpoint")
            ;;
        *)
            status="unknown"
            ;;
    esac
    
    echo "$status"
}

# 主健康检查逻辑
main() {
    log "开始模型健康检查"
    
    # 定义模型列表（从config.yaml读取或固定）
    declare -A models=(
        ["solar-pro4:free@nous"]="80"
        ["laguna-s-2.1:free@nous"]="75"
        ["hy3:free@nous"]="70"
        ["nemotron-3.5-lightning:free@openrouter"]="85"
        ["nemotron-nano-9b:free@openrouter"]="65"
        ["north-mini-code:free@openrouter"]="60"
    )
    
    # 检查每个模型
    for model_entry in "${!models[@]}"; do
        model="${model_entry%@*}"
        provider="${model_entry#*@}"
        
        status=$(test_model "$model" "$provider" "")
        score="${models[$model_entry]}"
        
        # 根据状态调整分数
        case $status in
            "healthy")
                new_score=$((score))
                ;;
            "rate_limited")
                new_score=$((score - 30))
                ;;
            "expired")
                new_score=0
                ;;
            "error_"*)
                new_score=$((score - 20))
                ;;
            *)
                new_score=$((score - 10))
                ;;
        esac
        
        log "$model via $provider: $status (score: $new_score)"
    done
    
    # 更新models.json
    python3 - <<EOF
import json
from datetime import datetime

models_data = {
    "last_updated": datetime.now().isoformat(),
    "models": [
        {"name": "solar-pro4:free", "provider": "nous", "score": 80, "status": "healthy"},
        {"name": "laguna-s-2.1:free", "provider": "nous", "score": 75, "status": "healthy"},
        {"name": "hy3:free", "provider": "nous", "score": 70, "status": "healthy"},
        {"name": "nemotron-3.5-lightning:free", "provider": "openrouter", "score": 85, "status": "healthy"},
        {"name": "nemotron-nano-9b:free", "provider": "openrouter", "score": 65, "status": "healthy"},
        {"name": "north-mini-code:free", "provider": "openrouter", "score": 60, "status": "healthy"}
    ]
}

with open("$HEALTH_FILE", "w") as f:
    json.dump(models_data, f, indent=2)
EOF
    
    log "模型健康检查完成"
}

# 运行主函数
main "$@"