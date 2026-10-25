# 客户端模型配置：Claude Code + Cursor（免费轮询 + OpenAI 兜底）

实测可用的配置模式（2026-08-24 验证）。目标：客户端默认走**免费模型轮询**，用户可**自选 OpenAI（Azure gpt-5-mini）兜底**，零费用优先。

## 凭据来源
- Nous / OpenRouter key：`~/.hermes/.env`
- Azure OpenAI 端点 + key：`/home/note.txt`（CC 用 AZ1 经 cc2azure 代理，Cursor 用 AZ2 直连）
- cc2azure 代理：`/home/ubuntu/.hermes/deploy/cc2azure.py`，服务 `cc2azure.service`（:4000）
- 注：本机 `oci` CLI 在 `/home/ubuntu/oci-monitor/venv/bin/oci`，需 `source venv/bin/activate` 或加 PATH

## Claude Code（`~/.claude/settings.json`）
- 设 `ANTHROPIC_BASE_URL=http://localhost:4000` + 任意 `ANTHROPIC_API_KEY` → 经 cc2azure 代理转 Azure gpt-5-mini（OpenAI 兜底）
- 免费轮询清单写在 `alternatives.free_routers`（格式 `base_url|model|KEYENV`），默认只用 nous 池 5 个（见下"稳定清单"）
- 实测：`claude` v2.1.238 已装；`curl :4000/v1/messages` → Azure gpt-5-mini HTTP 200 ✅

## Cursor（`~/.cursor/settings.json`）
- `providers.free_poll`：type=openai-compatible，strategy=round-robin，models 列 nous 池 5 个（api_key_env 指向 env 里的 NOUS_API_KEY）
- `providers.openai_fallback`：type=azure-openai，base_url 含 `api-version=2025-04-01-preview`，model=gpt-5-mini，api_key=AZ2 直连
- 实测：Azure gpt-5-mini 直连 HTTP 200 ✅

## 稳定免费轮询清单（nous 池，长期 200）
1. tencent/hy3:free
2. upstage/solar-pro4:free
3. poolside/laguna-s-2.1:free
4. stepfun/step-3.7-flash:free
5. meituan/longcat-2.0:free

> OpenRouter 池**不进主轮询链**（会整层瞬时全挂，见 openrouter-free-models.md 坑）。

## 验证清单（交付前必跑）
1. `claude -p "用中文说：配置成功"` → 走默认免费轮询应返回
2. CC 切 OpenAI：`export ANTHROPIC_BASE_URL=http://localhost:4000` 再跑同条 → 经 Azure 返回
3. Cursor：Settings 看 `free_poll` 为默认；选 `openai_fallback` 应走 Azure 返回
4. 存活探测：对 nous 5 模型逐个 `curl .../chat/completions` 确认 200（见 SKILL.md watchdog 脚本逻辑）

## OpenAI 兜底注意
- Azure gpt-5-mini 经 api-version=2025-04-01-preview 默认把 token 全烧在推理上 → content 空（部署特性，非配置错）。
- cc2azure 代理已处理 `reasoning_effort:low`；Cursor 直连时需在请求体带 `reasoning_effort:low` 才能拿正文。
- Azure FOUNDRY key 是资源级，**读不到订阅 consumption API**（401）→ 花费追踪用 `scripts/azure_spend_guard.sh` 本地账本（每次 delegate 后 record 一笔）。
