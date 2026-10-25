# OpenRouter 免费模型实测清单（2026-08-24 核实）

> 供 `scripts/daily_free_model_research.sh` 的质量核实依据。OpenRouter 无公开 JSON 榜单 API（Artificial Analysis 为 JS 渲染 HTML），故"实测可用候选"需在对话里 web_search 二次核实热度后再决定是否加入队列。

## 实测可用（HTTP 200，走 openrouter.ai + OR key）
- `nvidia/nemotron-3.5-lightning:free` — 1M ctx，快
- `nvidia/nemotron-3-super-120b-a12b:free` — 262K
- `nvidia/nemotron-nano-12b-v2-vl:free` — 128K 多模态
- `nvidia/nemotron-nano-9b-v2:free` — 128K
- `cohere/north-mini-code:free` — 256K 代码向
- `poolside/laguna-xs-2.1:free` — 262K
- `dots-studio/dots-3-note-preview:free` — 512K
- `liquid/lfm-2.5-2.6b:free` — 65K 小快
- `nvidia/nemotron-3-nano-30b-a3b:free` — ⭐ 强推（见下）
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` — 多模态推理
- `thinkingmachines/inkling:free` — 质量未明，排末尾观察

## 实测不可用（已剔除，勿再加）
- `z-ai/glm-5.2:free` — nous 端点 404 / OR 端点 429（上游 Decart 共享池限流，BYOK 无效）
- `google/gemma-4-26b-a4b-it:free` / `gemma-4-31b-it:free` — OR 429
- `thinkingmachines/inkling-small:free` — OR 403
- `nvidia/nemotron-3.5-content-safety:free` — 非对话模型（安全过滤），不加

## 横向对比结论（Artificial Analysis / 官方 benchmark）
- **nemotron-3-nano-30b-a3b**：AA Intelligence Index 14.5（超 9% 模型）、Coding 13%、Agentic 11%；社区实测 AIME2025=89.1% 超 Qwen3-30B；1M ctx RULER 68.2% 保持率；66 tok/s。Nvidia 新一代 MoE，性价比极高 → 排 OR 池前部。
- **nemotron-nano-omni**：多模态（图+文），增强多模态覆盖。
- **content-safety**：安全过滤模型，非对话，排除。
- **inkling**（完整版）：Thinking Machines 新模型，质量未明，排末尾观察。

## OpenRouter 限流须知
- 免费账号 50 次/天（未购 credit）→ 购 ≥$10 credit 后 1000 次/天，20 次/分。
- BYOK 仅付费模型生效；免费模型走上游共享池，你的 key 不增加额度，上游满载返 `upstream_429`。
- 故 OR 池也受上游波动，但分属不同 provider 不与 nous 池共沉（A 家限流不影响 B 家）。

## ⚠️ 实测坑：OR 免费池可整层瞬时全挂（2026-08-24 验证）
- 当日下午实测：OpenRouter 全部 15 个 `:free` 模型**同时**返回 429/404（探测 0 个存活），而 nous 池 5 个全 200。
- 含义：不要把 OR 池模型放进"强依赖"轮询链——它会在你最不期望时整体消失。
- 对策：客户端/路由配置的**免费轮询默认只用 nous 池**（hy3/solar-pro4/poolside/stepfun/meituan，长期稳定）；OR 池作"有就用、没有就跳过"的补充，不进主链。
- **发布型配置务必先复测再交付**：本会话曾先写好含 OR 模型的 Cursor/CC 配置，随后实测 OR 全挂 → 配置当场作废。任何"写配置给工具用"的动作，先跑一遍存活探测，用**当下存活**的模型填充，别用历史清单。

## 客户端配置（Claude Code / Cursor）技巧见 references/client-config-cc-cursor.md
