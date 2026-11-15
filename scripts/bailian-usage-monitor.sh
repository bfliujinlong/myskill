#!/bin/bash
# 百炼 Token Plan 用量监控脚本
# 记录每次调用的 token 消耗到本地账本，定期播报到 Telegram

source ~/.hermes/.env 2>/dev/null

LEDGER="$HOME/.hermes/scripts/bailian_usage_ledger.json"
BALANCE_FILE="$HOME/.hermes/scripts/bailian_balance.json"

# 套餐信息 (根据你的订阅修改)
PLAN_NAME="Lite"
PLAN_CREDITS=2500
PLAN_PERIOD_DAYS=7
PLAN_PRICE=39

# 读取当前周期已用 (从账本)
if [ -f "$LEDGER" ]; then
    USED_TODAY=$(python3 -c "
import json
from datetime import datetime, timedelta
try:
    with open('$LEDGER') as f:
        data = json.load(f)
    today = datetime.now().strftime('%Y-%m-%d')
    used = sum(e.get('credits', 0) for e in data.get('entries', []) if e.get('date','').startswith(today))
    total = sum(e.get('credits', 0) for e in data.get('entries', []))
    # 当前7天周期
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    period_used = sum(e.get('credits', 0) for e in data.get('entries', []) if e.get('date','') >= week_ago)
    print(f'{period_used:.2f}')
except:
    print('0')
" 2>/dev/null)
else
    USED_TODAY=0
    PERIOD_USED=0
fi

PERIOD_USED=${USED_TODAY:-0}
REMAINING=$(python3 -c "print(f'{${PLAN_CREDITS} - ${PERIOD_USED}:.2f}')" 2>/dev/null || echo "N/A")
USAGE_PCT=$(python3 -c "print(f'{${PERIOD_USED}/${PLAN_CREDITS}*100:.1f}')" 2>/dev/null || echo "N/A")

echo "📊 百炼 Token Plan 用量报告"
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo "套餐: ${PLAN_NAME} (¥${PLAN_PRICE}/月)"
echo "周期额度: ${PLAN_CREDITS} Credits / ${PLAN_PERIOD_DAYS}天"
echo ""
echo "📈 本周期已用: ${PERIOD_USED} Credits"
echo "📉 本周期剩余: ${REMAINING} Credits"
echo "📊 使用率: ${USAGE_PCT}%"
echo ""
if [ "${USAGE_PCT%.*}" -ge 80 ] 2>/dev/null; then
    echo "⚠️ 已用超80%，注意控制用量！"
elif [ "${USAGE_PCT%.*}" -ge 50 ] 2>/dev/null; then
    echo "🟡 已用超50%"
else
    echo "🟢 用量正常"
fi
