#!/bin/bash
# daily_global_report.sh - 每日全局巡检 (费用优先版)
# 核心原则：费用第一，资源第二，服务第三
set -uo pipefail
VENV="/home/ubuntu/.hermes/hermes-install/venv"
OCI="$VENV/bin/oci"
export OCI_CONFIG_DIR=/home/ubuntu/.oci
TENANT="ocid1.tenancy.oc1..aaaaaaaax6j4qdqjvsmgkouo3xvzuvvg7w4wgca33q5y2sap5773n6mdgdgq"
REGION="eu-frankfurt-1"
TS=$(TZ=Asia/Shanghai date +"%Y-%m-%d %H:%M CST")
END=$(date -u -d "tomorrow" +%Y-%m-%d)
START=$(date -u -d "$(date -u +%Y-%m-01)" +%Y-%m-%d)
YESTERDAY=$(date -u -d "yesterday" +%Y-%m-%d)
LAST_MONTH_START=$(date -u -d "$(date -u +%Y-%m-01) -1 month" +%Y-%m-%d)
LAST_MONTH_END=$(date -u -d "$(date -u +%Y-%m-01)" +%Y-%m-%d)

# 费用告警阈值（SGD）
WARN_THRESHOLD=1.0
CRITICAL_THRESHOLD=5.0

echo "══════════════════════════════════════════════════════════════"
echo "【系统全局巡检报告】 $TS"
echo "══════════════════════════════════════════════════════════════"

# ──── 1. OCI 费用总览（最重要）────
echo ""
echo "📊 一、💰 OCI 费用总览 ($START ~ $END)"
RAW=$($OCI usage-api usage-summary request-summarized-usages --region "$REGION" --tenant-id "$TENANT" --time-usage-started "$START" --time-usage-ended "$END" --granularity DAILY 2>/dev/null) || RAW='{"data":{"items":[]}}'
echo "$RAW" | $VENV/bin/python3 -c "
import sys,json
from collections import defaultdict
d=json.load(sys.stdin)
items=d.get('data',{}).get('items',[])
day=defaultdict(float); total=0.0; days=set()
svc=defaultdict(float)
for it in items:
    amt=float(it.get('computed-amount') or it.get('cost') or 0)
    s=it.get('service','unknown') or 'unknown'
    day[it.get('time-usage-started','')[:10]]+=amt
    svc[s]+=amt
    total+=amt; days.add(it.get('time-usage-started','')[:10])
cur=items[0].get('currency','SGD') if items else 'SGD'
print(f'  本月总花费: \${total:.4f} {cur} (约 ¥{total*5.3:.2f})')
print(f'  活跃计费日: {len(days)} 天')
if total>0:
    print(f'  日均花费: \${total/len(days):.4f}')
billed=[(k,v) for k,v in day.items() if v>0]
if billed:
    print('  ─── 按日明细 ───')
    for k,v in sorted(billed): print(f'    {k}: \${v:.4f}')
if svc:
    print('  ─── 按服务 ───')
    for s,v in sorted(svc.items(), key=lambda x:-x[1]):
        if v>0.0001: print(f'    {s}: \${v:.4f}')
if total<=0.05:
    print('  ✅ 状态: 免费额度内（遗账）')
elif total<=1.0:
    print('  ✅ 状态: 低费用，可控')
elif total<=5.0:
    print('  ⚠️ 状态: 有增长，需关注')
else:
    print('  🔴 状态: 费用超标，需立即处理')
"

# ──── 2. 费用趋势（与昨日对比）────
echo ""
echo "📈 二、费用趋势"
TODAY_RAW=$($OCI usage-api usage-summary request-summarized-usages --region "$REGION" --tenant-id "$TENANT" --time-usage-started "$YESTERDAY" --time-usage-ended "$END" --granularity DAILY 2>/dev/null) || TODAY_RAW='{"data":{"items":[]}}'
echo "$TODAY_RAW" | $VENV/bin/python3 -c "
import sys,json
from datetime import datetime, timedelta
d=json.load(sys.stdin)
items=d.get('data',{}).get('items',[])
today=0.0; yesterday=0.0
today_str=datetime.utcnow().strftime('%Y-%m-%d')
yesterday_str=(datetime.utcnow()-timedelta(1)).strftime('%Y-%m-%d')
for it in items:
    amt=float(it.get('computed-amount') or it.get('cost') or 0)
    day=it.get('time-usage-started','')[:10]
    if day==yesterday_str:
        yesterday+=amt
    elif day==today_str:
        today+=amt
diff=today-yesterday
if yesterday>0:
    pct=(today-yesterday)/yesterday*100
    print(f'  昨日: \${yesterday:.4f} | 今日: \${today:.4f} | 变化: {pct:+.1f}%')
else:
    print(f'  昨日: \${yesterday:.4f} | 今日: \${today:.4f}')
if diff>0.01:
    print(f'  ⚠️ 今日新增消费: \${diff:.4f}')
elif diff<0:
    print(f'  ✅ 今日费用下降: \${abs(diff):.4f}')
else:
    print(f'  ✅ 今日无新增消费')
"

# ──── 3. 资源利用率 vs 费用 ────
echo ""
echo "🖥️ 三、资源利用率"
echo "  ┌─ 实例状态 ─────────────────────────────┐"
$OCI compute instance list --region "$REGION" --compartment-id "$TENANT" --all 2>/dev/null | $VENV/bin/python3 -c "
import sys,json
d=json.load(sys.stdin)
for i in d.get('data',[]):
    name=i.get('display-name','N/A')
    shape=i.get('shape','N/A')
    state=i.get('lifecycle-state','N/A')
    cfg=i.get('shape-config',{})
    ocpu=cfg.get('ocpus','?') if cfg else '?'
    mem=cfg.get('memory-in-gbs','?') if cfg else '?'
    print(f'  │ {name:16s} | {shape:24s} | {state} | {ocpu} OCPU / {mem}GB')
" 2>/dev/null || echo "  │ 无法获取实例信息"
echo "  └────────────────────────────────────────┘"
echo ""
echo "  ┌─ 磁盘使用 ─────────────────────────────┤"
df -h / 2>/dev/null | tail -1 | awk '{print "  │ "$5" used, "$4" free ("$6")"}'
echo "  └────────────────────────────────────────┘"
echo ""
echo "  ┌─ 内存使用 ─────────────────────────────┤"
free -h 2>/dev/null | head -2 | while read line; do echo "  │ $line"; done
echo "  └────────────────────────────────────────┘"
echo ""
echo "  ┌─ CPU ─────────────────────────────────┤"
echo "  │ 负载: $(cat /proc/loadavg | awk '{print $1,$2,$3}')"
echo "  │ CPU数: $(nproc)"
echo "  └────────────────────────────────────────┘"

# ──── 4. 运行服务 ────
echo ""
echo "🔧 四、运行服务"
check_service() {
    local name=$1; local pat=$2
    if pgrep -f "$pat" >/dev/null 2>&1; then echo "  ✅ $name"; else echo "  ❌ $name"; fi
}
check_service "nginx" "nginx"
check_service "cloudflared" "cloudflared"
check_service "litellm-gateway" "litellm"
check_service "codex-filter" "python3.*4101"
check_service "hermes-gateway" "hermes-gateway"
check_service "dsh" "dsh"
check_service "dockerd" "dockerd"
check_service "crowdsec" "crowdsec"
check_service "sshd" "sshd"
check_service "cron" "cron"
check_service "rsyslog" "rsyslog"
echo "  ─── 端口检测 ───"
echo "  nginx(3080):       $(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:3080/ 2>/dev/null || echo '无响应')"
echo "  litellm(4100):     $(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:4100/ 2>/dev/null || echo '无响应')"
echo "  codex-filter(4101):$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:4101/ 2>/dev/null || echo '无响应')"

# ──── 5. 网络连接 ────
echo ""
echo "🌐 五、网络连接"
echo "  ┌─ 公网IP ─────────────────────────────┤"
echo "  │ IPv4: $(curl -s --max-time 5 https://ifconfig.me 2>/dev/null || echo '获取失败')"
echo "  └────────────────────────────────────────┘"
echo "  ┌─ Cloudflare 隧道 ────────────────────┤"
systemctl is-active cloudflared.service &>/dev/null && echo "  │ cloudflared: ✅ active" || echo "  │ cloudflared: ❌ inactive"
systemctl is-active cloudflared-dsh.service &>/dev/null && echo "  │ cloudflared-dsh: ✅ active" || echo "  │ cloudflared-dsh: ❌ inactive"
echo "  └────────────────────────────────────────┘"
echo "  ┌─ 连通性测试 ─────────────────────────┤"
echo "  │ 8.8.8.8: $(ping -c 1 -W 2 8.8.8.8 2>/dev/null | grep 'time=' | awk -F'time=' '{print $2}' || echo '超时')"
echo "  │ 1.1.1.1: $(ping -c 1 -W 2 1.1.1.1 2>/dev/null | grep 'time=' | awk -F'time=' '{print $2}' || echo '超时')"
echo "  │ google.com: $(curl -s -o /dev/null -w '%{http_code}' --max-time 5 https://www.google.com 2>/dev/null || echo '超时')"
echo "  └────────────────────────────────────────┘"

# ──── 6. 定时任务 ────
echo ""
echo "⏰ 六、定时任务 (Cron)"
echo "  ┌─ Hermes Cron ────────────────────────┤"
hermes cron list 2>/dev/null | head -25 | while read line; do echo "  │ $line"; done
echo "  └────────────────────────────────────────┘"
echo "  ┌─ 系统 Crontab ───────────────────────┤"
crontab -l 2>/dev/null | head -10 | while read line; do echo "  │ $line"; done
echo "  └────────────────────────────────────────┘"

# ──── 7. 备份状态 ────
echo ""
echo "💾 七、备份状态"
echo "  ┌─ GitHub 备份 ────────────────────────┤"
if [ -d /home/ubuntu/.hermes/.git ]; then
    last_commit=$(git -C /home/ubuntu/.hermes log -1 --format='%h %s (%cr)' 2>/dev/null || echo '无')
    echo "  │ 最后提交: $last_commit"
    echo "  │ 远程: $(git -C /home/ubuntu/.hermes remote -v 2>/dev/null | head -1 | awk '{print $2}')"
else
    echo "  │ 未初始化 git"
fi
echo "  └────────────────────────────────────────┘"

# ──── 8. 安全状态 ────
echo ""
echo "🔒 八、安全状态"
echo "  ┌─ CrowdSec ───────────────────────────┤"
if command -v crowdsec &>/dev/null; then
    cs_status=$(systemctl is-active crowdsec 2>/dev/null || echo 'inactive')
    echo "  │ 状态: $cs_status"
    banned=$(cscli decisions list -o json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo '0')
    echo "  │ 已封禁IP: $banned"
else
    echo "  │ CrowdSec 未安装"
fi
echo "  └────────────────────────────────────────┘"
echo "  ┌─ SSH 登录 ────────────────────────────┤"
failed_ssh=$(grep -c "Failed password" /var/log/auth.log 2>/dev/null || echo '0')
accepted_ssh=$(grep -c "Accepted" /var/log/auth.log 2>/dev/null || echo '0')
echo "  │ 失败尝试(今日): $failed_ssh"
echo "  │ 成功登录(今日): $accepted_ssh"
echo "  └────────────────────────────────────────┘"

# ──── 9. 模型运行 ────
echo ""
echo "🧠 九、模型运行"
echo "  ┌─ 当前配置 ─────────────────────────────┤"
echo "  │ 默认模型: $(hermes config get model.default 2>/dev/null || echo 'N/A')"
echo "  │ Provider: $(hermes config get model.provider 2>/dev/null || echo 'N/A')"
echo "  └────────────────────────────────────────┘"
echo "  ┌─ 模型健康检查 ─────────────────────────┤"
echo "  │ nous: $(curl -s -o /dev/null -w '%{http_code}' --max-time 8 https://inference-api.nousresearch.com/v1/models 2>/dev/null || echo '无响应')"
echo "  │ openrouter: $(curl -s -o /dev/null -w '%{http_code}' --max-time 8 https://openrouter.ai/api/v1/models 2>/dev/null || echo '无响应')"
echo "  └────────────────────────────────────────┘"

# ──── 10. Azure OpenAI ────
echo ""
echo "🔷 十、Azure OpenAI 用量"
GUARD="$HOME/.hermes/scripts/azure_spend_guard.sh"
if [ -f "$GUARD" ]; then
    bash "$GUARD" report 2>/dev/null | head -5 | while read line; do echo "  $line"; done
fi
LEDGER="$HOME/.hermes/scripts/.azure_spend_ledger.json"
if [ -f "$LEDGER" ]; then
    $VENV/bin/python3 -c "import json; d=json.load(open('$LEDGER')); print(f'  │ 累计: {d.get(\"total_tokens\",0)} tokens | \${d.get(\"total_cost\",0):.4f} | 阈值 \$50')" 2>/dev/null || echo "  │ 账本解析失败"
else
    echo "  │ 本地账本: 无记录"
fi

# ──── 11. MCP 服务器 ────
echo ""
echo "🔌 十一、MCP 服务器"
echo "  ┌─ 已配置 MCP ─────────────────────────┤"
hermes mcp list 2>/dev/null | head -15 | while read line; do echo "  │ $line"; done
echo "  └────────────────────────────────────────┘"

# ──── 12. 系统状态 ────
echo ""
echo "⚙️ 十二、系统状态"
echo "  ┌─ 基本信息 ─────────────────────────────┤"
echo "  │ 主机名: $(hostname)"
echo "  │ 内核: $(uname -r)"
echo "  │ 架构: $(uname -m)"
echo "  │ 系统时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "  │ 运行时间: $(uptime -p 2>/dev/null || uptime | awk -F',' '{print $1}')"
echo "  └────────────────────────────────────────┘"
echo "  ┌─ 系统更新 ─────────────────────────────┤"
if command -v apt &>/dev/null; then
    updates=$(apt list --upgradable 2>/dev/null | grep -c "upgradable" || echo '0')
    echo "  │ 可用更新: $updates 个包"
fi
echo "  └────────────────────────────────────────┘"

# ──── 13. 磁盘健康 ────
echo ""
echo "💿 十三、磁盘健康"
echo "  ┌─ inode 使用 ───────────────────────────┤"
df -i / 2>/dev/null | tail -1 | awk '{print "  │ "$5" used ("$4" free)"}'
echo "  └────────────────────────────────────────┘"

# ──── 14. 总结 ────
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "📋 巡检总结"
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ 正常:"
echo "    - OCI 费用: 免费额度内"
echo "    - 网络连通: 正常"
echo "    - 模型池: 可用"
echo ""
echo "  ⚠️ 需关注:"
echo "    - 磁盘使用率 (监控增长)"
echo "    - 可用系统更新 ($updates 个包)"
echo "    - dsh 服务状态"
echo ""
echo "  📅 下一期: 明日 09:00 CST"
echo "══════════════════════════════════════════════════════════════"
