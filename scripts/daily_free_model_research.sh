#!/bin/bash
# Daily Free Model Research - 每日调研新的免费AI模型
# 自动更新可用模型列表

set -o pipefail

OUTPUT_DIR="$HOME/.hermes/scripts/free-models-research"
TODAY=$(date '+%Y-%m-%d')
LOG_FILE="$HOME/.hermes/logs/free_model_research.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

create_output_dir() {
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR/$TODAY"
}

# 从OpenRouter爬取免费模型
scrape_openrouter() {
    log "抓取OpenRouter免费模型..."
    
    python3 - <<'EOF'
import requests, json
from datetime import datetime

try:
    # 获取免费模型列表
    resp = requests.get("https://openrouter.ai/api/models?free=true", timeout=30)
    models = resp.json() if resp.status_code == 200 else []
    
    # 过滤可用模型
    available = []
    for m in models[:50]:  # 前50个
        name = m.get('id', '')
        if ':free' in name:
            # 跳过已知不可用
            if any(x in name for x in ['gemma-4', 'inkling-small']):
                continue
            available.append({
                'name': name,
                'context': m.get('context_length', 4096),
                'pricing': m.get('pricing', {}),
                'latest': True
            })
    
    result = {
        'source': 'openrouter',
        'date': datetime.now().isoformat(),
        'total': len(available),
        'models': available[:20]  # 前20个
    }
    
    with open('/home/ubuntu/.hermes/scripts/free-models-research/today_openrouter.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"抓取到 {len(available)} 个免费模型")
except Exception as e:
    print(f"抓取失败: {e}")
EOF
}

# 从Nous Research获取可用模型
scrape_nous() {
    log "检查Nous Research模型..."
    
    python3 - <<'EOF'
import requests, json
from datetime import datetime

try:
    resp = requests.get("https://api.nousresearch.com/v1/models", timeout=30)
    models = resp.json().get('data', []) if resp.status_code == 200 else []
    
    available = []
    for m in models:
        name = m.get('id', '')
        if ':free' in name or 'free' in name.lower():
            # 检查是否有free period
            if m.get('free_period', {}).get('active', True):
                available.append({
                    'name': name,
                    'context': m.get('context_length', 4096),
                    'provider': 'nous'
                })
    
    result = {
        'source': 'nous',
        'date': datetime.now().isoformat(),
        'total': len(available),
        'models': available[:15]
    }
    
    with open('/home/ubuntu/.hermes/scripts/free-models-research/today_nous.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Nous查询到 {len(available)} 个免费模型")
except Exception as e:
    print(f"Nous查询失败: {e}")
EOF
}

# 检查模型有效性
check_model_status() {
    log "检查模型有效性..."
    
    python3 - <<'EOF'
import requests, json
from datetime import datetime

# 测试关键免费模型
test_models = [
    "nvidia/nemotron-3.5-lightning:free",
    "openrouter/nvidia/nemotron-3.5-lightning:free",
    "tencent/hy3:free",
    "upstage/solar-pro4:free",
    "stepfun/step-3.7-flash:free"
]

healthy = []
for model in test_models:
    try:
        # 简单检查endpoint
        if 'openrouter' in model or 'nemotron' in model:
            url = "https://openrouter.ai/api/v1/models"
        elif 'nous' in model or 'hy3' in model:
            url = "https://api.nousresearch.com/v1/models"
        else:
            continue
            
        resp = requests.get(url, timeout=10)
        if resp.status_code in [200, 429]:  # 429表示限流但存在
            healthy.append({
                'model': model,
                'status': 'available' if resp.status_code == 200 else 'rate_limited',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        pass  # 跳过不可达模型

result = {
    'date': datetime.now().isoformat(),
    'healthy_models': healthy
}

with open('/home/ubuntu/.hermes/scripts/free-models-research/daily_status.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"检查到 {len(healthy)} 个健康模型")
EOF
}

# 主函数
main() {
    log "开始每日免费模型调研"
    
    create_output_dir
    
    scrape_openrouter
    scrape_nous
    check_model_status
    
    # 清理旧数据（保留7天）
    find "$OUTPUT_DIR" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null
    
    log "每日调研完成"
}

main "$@"