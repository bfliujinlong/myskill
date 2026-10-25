#!/usr/bin/env bash
# free_model_watchdog.sh — 自动探测免费模型可用性, 把挂掉的排到 fallback 末尾, 可用的排前面
# 设计: 根治"免费模型被限流/无回复"反复发生. 每5分钟跑(由 cronjob 调), 零费用, 纯本地.
# 覆盖双端点: nous 池 (inference-api.nousresearch.com) + OpenRouter 池 (openrouter.ai, 用 OR key)
# 依赖: ~/.hermes/.env 里有 NOUS_API_KEY 和 OPENROUTER_API_KEY; hermes config 命令可用.
set -uo pipefail
HERMES_HOME="${HERMES_HOME:-/home/ubuntu/.hermes}"
cd "$HERMES_HOME" || exit 1
source .env 2>/dev/null || { echo "no .env"; exit 1; }

NOUS_BASE="https://inference-api.nousresearch.com/v1/chat/completions"
OR_BASE="https://openrouter.ai/api/v1/chat/completions"

# 主模型(始终置顶, 不进 fallback) + 全部备援, 格式 "provider|model"
ALL=(
  "nous|tencent/hy3:free"
  "nous|upstage/solar-pro4:free"
  "nous|poolside/laguna-s-2.1:free"
  "nous|stepfun/step-3.7-flash:free"
  "nous|meituan/longcat-2.0:free"
  "openrouter|nvidia/nemotron-3-nano-30b-a3b:free"
  "openrouter|nvidia/nemotron-3.5-lightning:free"
  "openrouter|nvidia/nemotron-3-super-120b-a12b:free"
  "openrouter|nvidia/nemotron-nano-12b-v2-vl:free"
  "openrouter|nvidia/nemotron-nano-9b-v2:free"
  "openrouter|cohere/north-mini-code:free"
  "openrouter|poolside/laguna-xs-2.1:free"
  "openrouter|dots-studio/dots-3-note-preview:free"
  "openrouter|liquid/lfm-2.5-2.6b:free"
  "openrouter|nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
  "openrouter|thinkingmachines/inkling:free"
)

probe () {
  local prov="$1" m="$2" base key code
  if [ "$prov" = "nous" ]; then
    base="$NOUS_BASE"; key="$NOUS_API_KEY"
  else
    base="$OR_BASE"; key="$OPENROUTER_API_KEY"
  fi
  code=$(curl -s -o /dev/null -w "%{http_code}" "$base" \
    -H "Authorization: Bearer $key" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":3}" --max-time 12)
  if [ "$code" = "200" ]; then echo "OK"; else echo "BAD:$code"; fi
}

GOOD=(); BAD=()
for entry in "${ALL[@]}"; do
  prov="${entry%%|*}"; m="${entry##*|}"
  st=$(probe "$prov" "$m")
  if [ "$st" = "OK" ]; then GOOD+=("$entry"); else BAD+=("$entry"); fi
done

# 构造 fallback_providers (主模型 hy3 不进 fallback; 其余可用在前, 坏的在后)
FB=""
for entry in "${GOOD[@]}" "${BAD[@]}"; do
  prov="${entry%%|*}"; m="${entry##*|}"
  [ "$m" = "tencent/hy3:free" ] && continue
  FB="${FB:+${FB},}{\"provider\":\"$prov\",\"model\":\"$m\"}"
done
NEW_FB="[$FB]"

hermes config set model.fallback_providers "$NEW_FB" >/dev/null 2>&1

TS=$(date '+%H:%M')
TOTAL=${#ALL[@]}
if [ "${#GOOD[@]}" -lt 3 ] || [[ " ${BAD[*]} " == *"tencent/hy3:free"* ]]; then
  MSG="⚠️ 免费模型大面积限流 @$TS | 可用:${#GOOD[@]}/$TOTAL | 坏:${BAD[*]:-无}"
  TOKEN=$(grep '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2)
  curl -s -o /dev/null "https://api.telegram.org/bot${TOKEN}/sendMessage?chat_id=5701842056&text=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$MSG")" --max-time 10
fi
echo "$TS good=${#GOOD[@]}/$TOTAL fallback=$NEW_FB"
