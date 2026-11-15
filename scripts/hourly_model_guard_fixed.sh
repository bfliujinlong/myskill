#!/bin/bash
# ── 每小时自动探测 + 重新排序免費模型（Nous + OpenRouter 雙端點）──
# 策略：
#   1) 同時探測 Nous 端點和 OpenRouter 端點
#   2) 每個端點挑出 HTTP 200 模型，按速度排序
#   3) 選全局最快的作 default，其它寫回 fallback
#   4) 永遠保留 nemotron-3.5-lightning:free 作為兜底
# ──────────────────────────────────────────────────────────────

set -euo pipefail

LOG="/tmp/hourly-model-guard-$(date +%Y%m%d-%H%M%S).log"
exec > "$LOG" 2>&1
echo "=== $(date) hourly-model-guard start ==="

ENV="/home/ubuntu/.hermes/.env"
CONFIG="/home/ubuntu/.hermes/config.yaml"

# 讀取兩個 key (容錯：若不存在則設空)
OR_KEY=$(grep -oP 'OPENROUTER_API_KEY=\K.*' "$ENV" 2>/dev/null | tr -d "'\"" | head -n1 || true)
NOUS_KEY=$(grep -oP 'NOUS_API_KEY=\K.*' "$ENV" 2>/dev/null | tr -d "'\"" | head -n1 || true)

# 若 key 為空，跳過該端點
if [ -z "$OR_KEY" ]; then echo "=> OR_KEY 为空，跳過 OpenRouter 探測"; fi
if [ -z "$NOUS_KEY" ]; then echo "=> NOUS_KEY 为空，跳過 Nous 探測"; fi

if [ -n "${OR_KEY:-}" ]; then echo "OR_KEY: ${OR_KEY}"; else echo "OR_KEY: (empty)"; fi
if [ -n "${NOUS_KEY:-}" ]; then echo "NOUS_KEY: ${NOUS_KEY:0:10}... (len=${#NOUS_KEY})"; else echo "NOUS_KEY: (empty)"; fi

# ── Nous 端點候選模型（按質量優先） ──────────────────────────
NOUS_CANDIDATES=(
  "solar-pro4:free"
  "solar-pro4"
  "solar-mini:free"
  "solar-mini"
  "tencent/hy3:free"
  "tencent/hy3"
  "tencent/hy4-preview:free"
  "tencent/hy4-preview"
  "tencent/hy1.5:free"
  "stepfun/step-3.7-flash"
  "meituan/longcat-2.0"
  "deepseek/deepseek-chat"
  "deepseek/deepseek-coder"
)

# ── OpenRouter 端點候選模型 ──────────────────────────────────
OR_CANDIDATES=(
  "minimax/minimax-m3:free"
  "minimax/minimax-m2.7:free"
  "nvidia/nemotron-3.5-lightning:free"
  "cohere/north-mini-code:free"
  "google/gemma-4-31b-it:free"
  "tencent/hy3:free"
  "meta-llama/llama-4-scout:free"
  "openai/gpt-4o-mini:free"
  "x-ai/grok-4.6:free"
  "google/gemini-3.7-flash:free"
  "google/gemini-3.1-pro-preview:free"
  "google/gemini-2.5-flash:free"
  "anthropic/claude-haiku-4.5:free"
  "anthropic/claude-sonnet-4.5:free"
  "meta-llama/llama-4-maverick:free"
  "sakana/fugu-ultra:free"
  "nvidia/nemotron-3-super-120b-a12b:free"
  "nvidia/nemotron-3-ultra-550b-a55b:free"
  "nvidia/nemotron-3-nano-30b-a3b:free"
  "poolside/laguna-s-2.1:free"
  "poolside/laguna-xs-2.1:free"
  "tencent/hy4-preview:free"
  "stepfun/step-3.7-flash:free"
  "meituan/longcat-2.0:free"
  "inclusionai/ling-3.0-flash-fin:free"
  "thinkingmachines/inkling:free"
  "thinkingmachines/inkling-small:free"
  "dots-studio/dots-3-note-preview:free"
  "liquid/lfm-2.5-2.6b:free"
  "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
  "nvidia/nemotron-3.5-content-safety:free"
  "meta/muse-spark-1.2:free"
  "deepseek/deepseek-v4-flash-0731:free"
  "deepseek/deepseek-v4-flash:free"
  "deepseek/deepseek-v4-pro-0813:free"
  "deepseek/deepseek-v4-pro:free"
  "qwen/qwen3.8-flash:free"
  "qwen/qwen3.8-max:free"
  "moonshotai/kimi-k3:free"
  "z-ai/glm-5.3-flash:free"
  "z-ai/glm-5.3:free"
  "z-ai/glm-5.2:free"
)

ANCHOR="nvidia/nemotron-3.5-lightning"
ALL_RESULTS=""

# ── 探測：Nous 端點 ──────────────────────────────────────────
echo ""
echo "=== 探測 Nous 端點 (${#NOUS_CANDIDATES[@]} 個) ==="
if [ -n "$NOUS_KEY" ]; then
  workdir_nous=$(mktemp -d)
  for c in "${NOUS_CANDIDATES[@]}"; do
    flat="${c//\//_}"
    probe_cmd="curl -s --max-time 8 -w '%{http_code}' -o '$workdir_nous/$flat.out' -H 'Authorization: Bearer ***' -H 'Content-Type: application/json' -d \"{\\\"model\\\":\\\"${c}:free\\\",\\\"messages\\\":[{\\\"role\\\":\\\"user\\\",\\\"content\\\":\\\"hi\\\"}],\\\"max_tokens\\\":8}\" 'https://inference-api.nousresearch.com/v1/chat/completions'"
    eval $probe_cmd 2>/dev/null || true
  done
  wait
  echo "Nous 探測完成"
  # 收集
  for f in "$workdir_nous"/*.out; do
    [ -f "$f" ] || continue
    while IFS= read -r line; do
      [ -n "$line" ] && ALL_RESULTS+="$line"$'\n'
    done < "$f"
  done
  rm -rf "$workdir_nous"
else
  echo "(跳過)"
fi

echo ""
echo "=== 探測 OpenRouter 端點 (${#OR_CANDIDATES[@]} 個) ==="
if [ -n "$OR_KEY" ]; then
  workdir_or=$(mktemp -d)
  for c in "${OR_CANDIDATES[@]}"; do
    flat="${c//\//_}"
    probe_cmd="curl -s --max-time 8 -w '%{http_code}' -o '$workdir_or/$flat.out' -H 'Authorization: Bearer ***' -H 'Content-Type: application/json' -d \"{\\\"model\\\":\\\"${c}:free\\\",\\\"messages\\\":[{\\\"role\\\":\\\"user\\\",\\\"content\\\":\\\"hi\\\"}],\\\"max_tokens\\\":8}\" 'https://openrouter.ai/api/v1/chat/completions'"
    eval $probe_cmd 2>/dev/null || true
  done
  wait
  echo "OpenRouter 探測完成"
  # 收集
  for f in "$workdir_or"/*.out; do
    [ -f "$f" ] || continue
    while IFS= read -r line; do
      [ -n "$line" ] && ALL_RESULTS+="$line"$'\n'
    done < "$f"
  done
  rm -rf "$workdir_or"
else
  echo "(跳過)"
fi

# ── 處理結果 ────────────────────────────────────────────────
echo ""
echo "=== 探測結果 ==="
TOTAL=$(( ${#NOUS_CANDIDATES[@]} + ${#OR_CANDIDATES[@]} ))
echo "總共探測 $TOTAL 個模型"

# 轉成數組
WORKING=()
while IFS= read -r line; do
  [ -n "$line" ] && WORKING+=("$line")
done <<< "$ALL_RESULTS"

# 按來源分組顯示
echo ""
echo "─── Nous 可用 ───"
NOUS_COUNT=0
for w in "${WORKING[@]}"; do
  case "$w" in
    nous*) echo "  $w"; NOUS_COUNT=$((NOUS_COUNT + 1)) ;;
  esac
done
if [ "$NOUS_COUNT" -eq 0 ]; then echo "  (無)"; fi

echo ""
echo "─── OpenRouter 可用 ───"
OR_COUNT=0
for w in "${WORKING[@]}"; do
  case "$w" in
    or*) echo "  $w"; OR_COUNT=$((OR_COUNT + 1)) ;;
  esac
done
if [ "$OR_COUNT" -eq 0 ]; then echo "  (無)"; fi

# 合併所有可用，按速度排序（第四個冒號分隔欄位是 ms）
WORKING_SORTED=()
if [ "${#WORKING[@]}" -gt 0 ]; then
  while IFS= read -r line; do
    [ -n "$line" ] && WORKING_SORTED+=("$line")
  done < <(printf '%s\n' "${WORKING[@]}" | sort -t: -k4 -n)
fi
WORKING=("${WORKING_SORTED[@]+"${WORKING_SORTED[@]}"}")

if [ "${#WORKING[@]}" -eq 0 ]; then
  echo ""
  echo "❌ 沒有任何模型可用！保留現有配置不動。"
  exit 0
fi

echo ""
echo "✅ 共 ${#WORKING[@]} 个模型可用（按響應速度排序）:"
echo ""
for w in "${WORKING[@]}"; do
  IFS=: read -r src m _ms <<< "$w"
  printf "  %-12s %-45s %5s ms\n" "$src" "$m" "$_ms"
done

# ── 組裝配置 ────────────────────────────────────────────────
echo ""
echo "=== 産出配置 ==="

ANCHOR_FOUND=0
FINAL_FB=()
for w in "${WORKING[@]}"; do
  IFS=: read -r src m _ms <<< "$w"
  if [ "$m" = "$ANCHOR" ]; then
    ANCHOR_FOUND=1
  else
    FINAL_FB+=("$w")
  fi
done

# 把 anchor 放最後
if [ "$ANCHOR_FOUND" -eq 1 ]; then
  for w in "${WORKING[@]}"; do
    IFS=: read -r src m _ms <<< "$w"
    if [ "$m" = "$ANCHOR" ]; then
      FINAL_FB+=("$w")
      break
    fi
  done
else
  # 找最慢的放最後（兜底）
  LAST_MS=0
  LAST_W=""
  for w in "${WORKING[@]}"; do
    IFS=: read -r src m _ms <<< "$w"
    if [ "$_ms" -gt "$LAST_MS" ]; then
      LAST_MS="$_ms"
      LAST_W="$w"
    fi
  done
  if [ -n "$LAST_W" ]; then
    FINAL_FB+=("$LAST_W")
  fi
fi

# 選最快的作主模型
PRIMARY_RAW="${FINAL_FB[0]}"
PRIMARY_SRC="${PRIMARY_RAW%%:*}"
# 取模型名（去掉前綴）
PRIMARY_MID="${PRIMARY_RAW#*|}"
PRIMARY_MODEL="${PRIMARY_MID%%:*}"

echo "主模型 → ${PRIMARY_MODEL} (${PRIMARY_SRC})"
echo "兜底模型 → ${ANCHOR}:free"

# 確定 provider 和 base_url
if [ "$PRIMARY_SRC" = "nous" ]; then
  PROVIDER="nous"
  BASE_URL="https://inference-api.nousresearch.com/v1"
  echo "寫入 config.yaml: provider=${PROVIDER} base_url=${BASE_URL}"
else
  PROVIDER="openrouter"
  BASE_URL="https://openrouter.ai/api/v1"
  echo "寫入 config.yaml: provider=${PROVIDER} base_url=${BASE_URL}"
fi

# ── 寫入 config.yaml ─────────────────────────────────────────
FALLBACK_MODELS=()
for w in "${FINAL_FB[@]}"; do
  IFS=: read -r _src m _ms <<< "$w"
  model_name="${m%:free}"
  FALLBACK_MODELS+=("$model_name")
done

if [ "${#FALLBACK_MODELS[@]}" -gt 0 ]; then
  python3 - "$CONFIG" "$PROVIDER" "$BASE_URL" "$PRIMARY_MODEL" "${FALLBACK_MODELS[@]}" <<'PYEOF'
import sys, yaml

config_path = sys.argv[1]
provider = sys.argv[2]
base_url = sys.argv[3]
primary_model = sys.argv[4]
fallback_models = sys.argv[5:]

config = yaml.safe_load(open(config_path))
config.setdefault("model", {})
config["model"]["default"] = primary_model
config["model"]["provider"] = provider
config["model"]["base_url"] = base_url

fb = [{"provider": provider, "model": m} for m in fallback_models]
config["model"]["fallback_providers"] = fb

with open(config_path, "w") as f:
    yaml.dump(config, f, sort_keys=False, allow_unicode=True, width=120)
print(f"寫入完成: default={primary_model}")
print(f"fallback 數量: {len(fb)}")
for e in fb:
    print(f"  - {e['model']}")
PYEOF
else
  echo "⚠️ 沒有 fallback 模型，需要至少保留一個"
fi

echo ""
echo "=== 完成 ($(date)) ==="
echo "日志: $LOG"