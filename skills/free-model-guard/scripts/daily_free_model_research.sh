#!/usr/bin/env bash
# daily_free_model_research.sh — 每日外网调研好用的免费模型, 对比推荐站, 给出"加不加队列"建议
# 设计: 配合 free_model_watchdog.sh (探活) 使用. 本脚本负责"发现新模型 + 横向对比 + 建议".
# 运行: 每日 cron (默认上海 09:10). 零费用, 纯本地 + 外网只读.
# 依赖: ~/.hermes/.env 里 NOUS_API_KEY + OPENROUTER_API_KEY; 机器能外网(经 Cloudflare 隧道)
set -uo pipefail
HERMES_HOME="${HERMES_HOME:-/home/ubuntu/.hermes}"
cd "$HERMES_HOME" || exit 1
source .env 2>/dev/null || { echo "no .env"; exit 1; }

TS=$(date '+%Y-%m-%d %H:%M %Z')
OR_KEY="${OPENROUTER_API_KEY:-}"
NOUS_KEY="${NOUS_API_KEY:-}"

# 当前队列里已有的模型 (从 config 取, 避免重复推荐)
CURRENT=$(hermes config get model 2>/dev/null)
in_queue () {
  local m="$1"
  [[ "$CURRENT" == *"$m"* ]] && return 0 || return 1
}

# 1) 拉 OpenRouter 全部免费模型 (结构化 JSON API)
mapfile -t OR_FREE < <(curl -s "https://openrouter.ai/api/v1/models" \
  -H "Authorization: Bearer $OR_KEY" --max-time 25 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); [print(m['id']) for m in d.get('data',[]) if m.get('id','').endswith(':free')]" 2>/dev/null)

echo "[$TS] OpenRouter free models found: ${#OR_FREE[@]}"

# 2) 实测存活 (走 openrouter.ai 端点, 带 key)
alive=()
for m in "${OR_FREE[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://openrouter.ai/api/v1/chat/completions" \
    -H "Authorization: Bearer $OR_KEY" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":3}" --max-time 12)
  [ "$code" = "200" ] && alive+=("$m")
done
echo "[$TS] OpenRouter free alive: ${#alive[@]}/${#OR_FREE[@]}"

# 3) 候选 = 存活 且 不在当前队列
candidates=()
for m in "${alive[@]}"; do
  in_queue "$m" || candidates+=("$m")
done

# 4) 横向对比推荐站 (web_search 拿 Artificial Analysis / 社区榜单结论, 日志留存)
RECOS=""
if [ ${#candidates[@]} -gt 0 ]; then
  QUERY="best free LLM API models 2026 Artificial Analysis ranking $(IFS=,; echo "${candidates[*]}")"
  # 用 hermes 的 web_search 能力较难在纯bash调, 退化为: 标记候选, 人工/下轮对话核对
  RECOS="候选需人工/AA榜核对: ${candidates[*]}"
fi

# 5) 组装报告发 Telegram
if [ ${#candidates[@]} -gt 0 ]; then
  MSG="🆕 每日免费模型调研 @$TS
OpenRouter 免费存活: ${#alive[@]}/${#OR_FREE[@]}
队列外新增候选(${#candidates[@]}):
$(printf '• %s\n' "${candidates[@]}")
建议: 以上实测 HTTP200 可用, 可加入 fallback 队列(尤其大上下文/多模态款).
横向对比: Artificial Analysis 等榜单请于对话中让我 web_search 核实热度后再加."
else
  MSG="✅ 每日免费模型调研 @$TS
OpenRouter 免费存活: ${#alive[@]}/${#OR_FREE[@]}
队列外无新增候选 (现有 ${#OR_FREE[@]} 免费模型均已覆盖)."
fi

TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2)
curl -s -o /dev/null "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=5701842056&text=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$MSG")" --max-time 10

# 6) 落本地日志 (供对话中复盘)
echo "$MSG" >> "$HERMES_HOME/logs/daily_free_model_research.log"
echo "[$TS] done. candidates=${#candidates[@]}"
