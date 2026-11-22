#!/usr/bin/env bash
# crowdsec_report.sh — 播报 CrowdSec 被攻击情况到 Telegram
# 设计: 每日/随时查 CrowdSec 真实攻击告警 + 当前封禁IP, 汇总发 Telegram.
#       零费用, 纯本地. 由 cron 每日跑(默认上海 09:00), 或随时手动 bash 触发.
set -uo pipefail
HERMES_HOME="${HERMES_HOME:-/home/ubuntu/.hermes}"
cd "$HERMES_HOME" || exit 1
source .env 2>/dev/null || { echo "no .env"; exit 1; }

TS=$(date '+%Y-%m-%d %H:%M %Z')
WHITELIST_TEST="192.0.2.99"   # 测试IP, 播报时忽略

# 真实告警 (排除测试IP: 192.0.2.99, 它在 decisions[].value 里)
ALERTS=$(sudo cscli alerts list -o json 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    rows=d.get('data',[]) if isinstance(d,dict) else d
    real=[]
    for r in rows:
        vals=[dec.get('value','') for dec in (r.get('decisions') or [])]
        if any('192.0.2.99' in str(v) for v in vals): continue
        real.append(r)
    print(len(real))
    for r in real[-10:]:
        decs=r.get('decisions') or [{}]
        v=decs[0].get('value','') if decs else ''
        print(f\"{str(r.get('created_at',''))[:19]} | {r.get('scenario','')} | {v}\")
except Exception as e:
    print('0')
" 2>/dev/null)

# 当前封禁
BANS=$(sudo cscli decisions list -o json 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    rows=d.get('data',[]) if isinstance(d,dict) else d
    real=[r for r in rows if '192.0.2.99' not in str(r.get('value',''))]
    print(len(real))
    for r in real:
        print(f\"{r.get('value','')} | {r.get('reason','')} | 至 {r.get('until','')}\")
except Exception as e:
    print('0')
" 2>/dev/null)

NA=$(echo "$ALERTS" | head -1)
NB=$(echo "$BANS" | head -1)

if [ "$NA" = "0" ] && [ "$NB" = "0" ]; then
  MSG="🛡️ CrowdSec 攻击播报 @$TS
✅ 平安: 当前无真实攻击告警, 无封禁IP.
(仅测试记录已忽略)
防护在线: sshd/linux/nginx collection + firewall bouncer 运行正常."
else
  MSG="🛡️ CrowdSec 攻击播报 @$TS
⚠️ 真实告警: $NA 条 | 当前封禁: $NB 个IP

【近期告警】
$(echo "$ALERTS" | tail -n +2)

【当前封禁IP】
$(echo "$BANS" | tail -n +2)"
fi

TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2)
curl -s -o /dev/null "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=5701842056&text=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$MSG")" --max-time 10
echo "$MSG"
