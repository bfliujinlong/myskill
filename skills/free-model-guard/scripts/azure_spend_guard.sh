#!/usr/bin/env bash
# azure_spend_guard.sh — Azure gpt-5-mini 本地账本 + 低额告警
# 背景: Azure FOUNDRY key 是资源级部署 key, 读不到订阅级 consumption API(401),
#       故用本地账本自记每次调用估算cost, 累加超阈值则发 Telegram 告警.
# 用法:
#   azure_spend_guard.sh record <reasoning_tokens>   # 记一笔调用 (delegate后调用)
#   azure_spend_guard.sh check                        # 仅检查阈值不发(调试)
#   azure_spend_guard.sh report                       # 报当前账本累计
# 设计: 零费用, 纯本地; 由 cron 每日跑 check 兜底.
set -uo pipefail
HERMES_HOME="${HERMES_HOME:-/home/ubuntu/.hermes}"
cd "$HERMES_HOME" || exit 1
source .env 2>/dev/null || { echo "no .env"; exit 1; }

LEDGER="$HERMES_HOME/logs/azure_spend_ledger.json"
THRESHOLD_USD=50          # 告警阈值 (Sponsorship $5000 内, 50刀算异常猛用)
# gpt-5-mini 标准定价 (USD/1M tok): 输入0.15 输出0.60, reasoning计入输出
PRICE_IN=0.15; PRICE_OUT=0.60
[ -f "$LEDGER" ] || echo '{"total_usd":0,"calls":0,"last":""}' > "$LEDGER"

case "${1:-check}" in
  record)
    rt="${2:-0}"; in_tok="${3:-0}"
    cost=$(python3 -c "print(round($in_tok/1e6*$PRICE_IN + $rt/1e6*$PRICE_OUT, 6))")
    python3 - "$LEDGER" "$cost" "$rt" <<'PY'
import json,sys,datetime
p,add,rt=sys.argv[1],float(sys.argv[2]),sys.argv[3]
d=json.load(open(p))
d['total_usd']=round(d['total_usd']+add,6)
d['calls']+=1
d['last']=datetime.datetime.utcnow().isoformat()+"Z rt="+rt
json.dump(d,open(p,'w'),indent=2)
print(f"recorded +${add} -> total ${d['total_usd']} ({d['calls']} calls)")
PY
    ;;
  report)
    python3 -c "import json;d=json.load(open('$LEDGER'));print(f\"Azure gpt-5-mini 累计: \${d['total_usd']} / {d['calls']} calls / 阈值 \${'$THRESHOLD_USD'} / last {d['last']}\")"
    ;;
  check|*)
    total=$(python3 -c "import json;print(json.load(open('$LEDGER'))['total_usd'])")
    if python3 -c "import sys;sys.exit(0 if float('$total')>=$THRESHOLD_USD else 1)"; then
      MSG="⚠️ Azure gpt-5-mini 累计消耗 \$${total} 已超阈值 \$${THRESHOLD_USD}！请检查 delegate 调用量。"
      TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2)
      curl -s -o /dev/null "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=5701842056&text=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$MSG")" --max-time 10
      echo "$MSG"
    else
      echo "OK total=\$${total} (under \$${THRESHOLD_USD})"
    fi
    ;;
esac
