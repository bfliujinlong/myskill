---
name: free-model-guard
description: "抗限流免费模型路由：litellm 网关统一轮询 nous 免费模型(质量排序+usage-based路由+健康探测)，Codex/Cursor/CC 经本地网关走免费模型零费用；难任务 delegate Azure gpt-5-mini。根治'免费模型限流/无回复'与'客户端连不上免费模型'。触发词: 限流/无回复/免费模型/router/加模型/codex免登录/cursor连免费/零费用."
version: 0.3.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [模型路由, 免费优先, 抗限流, litellm, codex, cursor, 成本控制]
    related_skills: [model-router, models, overseas-model-hub]
---

# 抗限流免费模型路由（Free Model Guard v0.3）

解决两类问题：(1) 免费模型被上游限流导致无回复；(2) 客户端（Codex/Cursor/CC）连不上免费模型或强制弹登录/付费。

**核心架构：一个 litellm 网关（:4100）统管所有免费模型 + 一个 tool-filter 代理（:4101）适配 Codex 的私有协议 → 所有客户端指向 localhost:4101，零费用、免登录、质量轮询。**

## 链路总览
```
任意客户端 (Codex / Cursor / CC / Hermes)
   → localhost:4101  (codex-tool-filter: 剥 tool + WS→403逼降级HTTPS)
   → localhost:4100  (litellm 网关: 质量路由 + 健康探测 + 故障转移)
   → nous 5 个免费模型 (solar>laguna>stepfun>meituan>hy3)
   → 零费用
可选: model="azure-gpt5mini" → Azure gpt-5-mini (Sponsorship $5000, 非免费但零信用卡)
```

## 组件与端口
| 组件 | 端口 | systemd service | 作用 |
|---|---|---|---|
| litellm 网关 | :4100 | `codex-free-proxy.service` | 多 deployment 同 model_name 自动轮询；usage-based-routing 按延迟/成功率选优；health_check 每2分钟剔除挂掉的 |
| tool-filter 代理 | :4101 | `codex-tool-filter.service` | Python http.server，清空请求里所有 `tools`（Codex 发 namespace/web_search 免费模型拒收），WS 升级返回 403 逼 Codex 降级 HTTPS |

## litellm 配置要点（scripts/litellm_config.yaml）
- **同一 `model_name: hy3` 挂 5 个 nous 免费 deployment**，顺序按质量：solar-pro4 > laguna-s-2.1 > stepfun-flash > meituan-longcat > hy3。litellm 自动轮询。
- **`router_settings.routing_strategy: "usage-based-routing"`**：按各部署延迟/成功率动态选最优，自然偏向高质量且快的（hy3 垫底，累积数据后降权）。
- **`general_settings.health_check: true` + `health_check_interval: 120`**：定期 ping，挂掉的自动剔除，恢复加回（注意 health_check 放 general_settings，不放 router_settings，否则启动报 `not a valid router_settings parameter`）。
- **`router_settings.drop_params: true`**：丢弃模型不支持的 param（如 namespace）。
- **别名 deployment**：`gpt-5.2/gpt-5.1/gpt-5/gpt-4o` 都映射到免费模型，让客户端切模型名时不 400。
- **⚠️ 别名必须指向 OpenRouter 免费模型，不能指向 nous**：nous 免费层强制要求请求带 `tags` 字段，而 Codex 的 `/v1/responses` 协议、litellm 转发都不自动补 tags → 全部 `gpt-5.x` 别名映射到 nous 时必报 `400 missing tags`（2026-08-30 实测 Codex 直接打不开）。**正确写法**：`gpt-5.2 → openrouter/nvidia/nemotron-3.5-lightning:free`、`gpt-5.1/gpt-4o → openrouter/cohere/north-mini-code:free`、`gpt-5 → openrouter/nvidia/nemotron-3.5-lightning:free`（均在 `litellm_params` 里 `api_key: os.environ/OPENROUTER_API_KEY`，**不要** `api_base`，让 litellm 走默认 OR 端点）。`hy3` 主 model_name 仍可走 nous 5 池（Hermes 用，Hermes 自己会补 tags）；但**凡客户端可能切到的 `gpt-*` 别名一律 OR 免费**。
- **`azure-gpt5mini`**：单独 model_name，Azure gpt-5-mini（`reasoning_effort: low`，否则该部署把 token 烧光返空）。
- `allow_requests_without_auth: true`：任意 key 都接受（客户端填占位 key 即可）。

## tool-filter 代理（scripts/codex_tool_filter.py）
- 监听 `:4101`，递归清空请求体所有 `tools` 字段（不只剥 namespace——保留 function/web_search/x_search 仍被 meituan 等拒收 → 400，故全部清空。Codex 本地自己跑 agentic 工具，模型只需出文本/代码，清空安全）。
- WS 升级请求（`Upgrade: websocket`）不处理 → 返回 403，Codex 收到后降级 HTTPS 成功连。
- **必须 `allow_reuse_address=True`**（否则 systemd `Restart=always` + 旧实例未退端口被抢 → `Address already in use` 死循环）。

## 客户端配置

### Codex（已验证免登录 TUI 可用）
`~/.codex/config.toml`（模板见 references/codex.config.toml.example）：
```toml
model = "gpt-5.2"                      # 映射到 solar 免费模型 (gpt-5.2 别名)
model_provider = "litellm"
model_reasoning_effort = "medium"
[model_providers.litellm]
name = "Local LiteLLM (free models)"
base_url = "http://127.0.0.1:4101/v1" # tool-filter
env_key = "OPENAI_API_KEY"             # 占位, litellm 免auth
wire_api = "responses"                 # Codex 用 /v1/responses 协议
[projects."/home/ubuntu"]
trust_level = "trusted"
```
- 同时 `~/.bashrc` 写 `export OPENAI_API_KEY="sk-<随机hex>"`（占位，须 `sk-` 开头像真 key，纯 `sk-local-xxx` 可能仍被 TUI 拒）。
- **免登录原理**：官方自定义 `model_providers.<name>` + `wire_api="responses"` 走本地 provider 模式，不弹 ChatGPT 登录。裸 `codex` 直接进 TUI 可用（model 显示 hy3/gpt-5.2，不弹登录）。
- 一次性任务：`codex exec --skip-git-repo-check -m "hy3" "任务"`（家目录需 `--skip-git-repo-check`，否则报 `Not inside a trusted directory`）。

### Cursor（OCI 桌面，已验证）
`~/.cursor/settings.json`（模板见 references/cursor.settings.json.example）：
- `free_poll` provider 的 models 全指向 `http://localhost:4101/v1`，model 填 `hy3`/`gpt-5.2`/`gpt-5.1`/`gpt-4o`（都映射到免费模型），`api_key_env: CURSOR_LOCAL_KEY`。
- `env.CURSOR_LOCAL_KEY = "sk-local-litellm-placeholder"`（litellm 免 auth，但 Cursor 要求非空）。
- Cursor 设置 → Models → 选 `free_poll` → 直接聊天/写代码走免费模型。

### Claude Code
CC 经 `cc2azure:4000` 转 **Azure gpt-5-mini**（Sponsorship 零信用卡，非免费模型）。CC 本身交互式不弹登录。若要 CC 也走免费模型，需另建 Anthropic→nous 代理（未建，已知缺口）。

### Hermes 全局路由
主 `tencent/hy3:free`(nous) + nous 池 4 fallback，看门狗每5分探测重排（见下）。cron job 模型须单独改成 hy3@nous（不继承全局，详见坑段）。

## 一键部署（换机器复现）
```bash
# 0) 前置: .env 含 NOUS_API_KEY, AZURE_OPENAI_API_KEY
# 1) 建 litellm 独立 venv + 装 [proxy]
python3 -m venv /home/ubuntu/.litellm-venv
source /home/ubuntu/.litellm-venv/bin/activate
pip install "litellm[proxy]"
deactivate

# 2) 复制 skill 的脚本与配置
SKILL=~/.hermes/skills/free-model-guard
cp $SKILL/scripts/litellm_config.yaml ~/.hermes/deploy/
cp $SKILL/scripts/codex_tool_filter.py ~/.hermes/deploy/
cp $SKILL/scripts/start_litellm.sh   ~/.hermes/deploy/
chmod +x ~/.hermes/deploy/start_litellm.sh
cp $SKILL/scripts/codex-free-proxy.service ~/.config/systemd/user/
cp $SKILL/scripts/codex-tool-filter.service ~/.config/systemd/user/

# 3) 写入客户端配置
cp $SKILL/references/codex.config.toml.example ~/.codex/config.toml
cp $SKILL/references/cursor.settings.json.example ~/.cursor/settings.json
echo 'export OPENAI_API_KEY="sk-'"$(python3 -c "import secrets;print(secrets.token_hex(24))")"'"' >> ~/.bashrc

# 4) 起服务
systemctl --user daemon-reload
systemctl --user enable --now codex-free-proxy.service
systemctl --user enable --now codex-tool-filter.service

# 5) 验证
curl -s -o /dev/null -w "litellm /v1/models -> %{http_code}\n" http://127.0.0.1:4100/v1/models
curl -s -X POST http://127.0.0.1:4101/v1/responses -H "Content-Type: application/json" \
  -d '{"model":"hy3","input":"hi"}' --max-time 30 -o /dev/null -w "filter -> %{http_code}\n"
codex exec --skip-git-repo-check -m "hy3" "用中文回四个字:配置成功"   # 应 EXIT=0
```

## 每日外网调研（发现新模型）
`scripts/daily_free_model_research.sh`：每日拉 OpenRouter 全量免费模型 → 实测存活 → 对比队列 → 发 Telegram。注册：`hermes cron create "10 1 * * *" --name "daily-free-model-research" --script "daily_free_model_research.sh" --no-agent`（上海 09:10）。Artificial Analysis 无公开 JSON API（JS 渲染），质量核实在对话中 `web_search` 做，勿盲加。

## Azure 花费追踪（scripts/azure_spend_guard.sh）
Azure FOUNDRY key 资源级，读不到订阅 consumption API（401）→ 本地账本自记。`record <tokens>` 记一笔；`check` 超 $50 发 Telegram；`report` 看累计。已注册每日 `check` cron（`azure-spend-guard`）。

## 已验证可用（2026-10-08，已加进路由/已验证 curl 200）
- **CF Workers AI**：`@cf/meta/llama-3.1-8b-instruct` / `@cf/mistralai/mistral-small-3.1-24b-instruct` / `@cf/meta/llama-3.3-70b-instruct-fp8-fast`（零额度，`cfut_` token，`chmod 600`，`--http1.1` 必须，非内置 provider 需手动配 `providers:` + `model:` + 独立 SSH 重启，已写 `references/cf-workers-ai.md`，已写 `cf_wai_check.sh`）
- **Mistral Free**：`ministral-8b-2512`（限速 ~1/min，已 200）
- **Ollama 本地**：`qwen3:4b` / `phi3.5:3.8b` / `deepseek-r1:1.5b`（断网可用，ARM 慢）
- **cb-official 混元**：`hy3`/`hy4-preview`（`CODEBUDDY_API_KEY`, 只混元可用，非混元 500，已记录限制）

## 已验证剔除的坏模型（勿再加）
- `z-ai/glm-5.2:free`：nous 404 / OR 429（Decart 共享池限流，BYOK 无效）
- `google/gemma-4-*:free`：OR 429
- `thinkingmachines/inkling-small:free`：OR 403
- OpenRouter 免费池可**整层瞬时全挂**（实测 15 个同时 429/404，nous 池 5 个全 200）→ 客户端默认轮询只用 nous 池；OR 池不进强依赖主链。
- **OpenRouter 免费模型状态变更（2026-08-30 实测）**：`nvidia/nemotron-3-nano-30b-a3b:free` 已**转付费**（404 "This model is unavailable for free"）；`nvidia/nemotron-nano-12b-v2-vl:free` 404；`liquid/lfm-2.5-2.6b:free` 429。**可用**：`nvidia/nemotron-3.5-lightning:free`（1M ctx，质量好）、`cohere/north-mini-code:free`。
- **Nous 免费层裸 REST 不可直连**：nous inference API 要求请求带 `tags`/`user` 字段（报 "missing tags"/"missing user tag"），OpenAI SDK 和 litellm 都不自动补 → 想用 nous 免费模型须走 litellm 网关（已配好 /v1 转发 + drop_params）或 Hermes 自己的 OAuth/nous SDK，不要裸 curl `inference-api.nousresearch.com/v1/chat/completions`。

## 坑（本会话实测）
- **litellm `health_check` 放错位置**：放 `router_settings` 启动报 `not a valid router_settings parameter`，必须放 `general_settings`。
- **litellm `router_settings.fallbacks` 格式**：`["a","b"]` / dict 映射都报 `not a dictionary` → 改用**同一 model_name 多个 deployment 条目**让 litellm 自动轮询（最稳）。
- **litellm `proxy_hooks` 的 `request_hook`/`response_api_request_hook` 对 `/v1/responses` 不调用** → tool 过滤不能靠 hook，必须用前面 tool-filter 反向代理。
- **Codex 的 `disabled_tools` / `CODEX_DISABLE_WEBSOCKETS` 环境变量不生效**（仍发 namespace + 仍试 WS）。
- **Codex 裸 `codex`（TUI）弹登录的根因** = auth.json 缺失 + 无有效 key。修法不是删 auth.json（那才导致弹登录），而是给**占位 key**（sk- 开头）+ 自定义 `model_providers.litellm` 本地 provider（不弹登录）。旧 SKILL 写"裸 codex 别用"已过时——现在自定义 provider 已修好，裸 `codex` 可用。
- **systemd 重启风暴**：filter 脚本 `allow_reuse_address=False` + `Restart=always` → 旧实例未退端口被抢死循环。须 `allow_reuse_address=True` + `systemctl stop` + `reset-failed` 干净重启。
- **Azure gpt-5-mini 作 Codex 后端会 429**（部署限流 + reasoning token 烧光），且过不了 namespace 之外的限制 → **Codex 默认走 nous 免费模型，勿用 Azure 当 Codex 默认**。`model="azure-gpt5mini"` 仅显式指定时兜底（需 `reasoning_effort: low`）。
- **Hermes gateway 不能自重启**（在 gateway 树内 `restart` 会被护栏拦截自杀）→ 改 config 后用户本机跑 `systemctl --user restart hermes-gateway.service`。
- **config.yaml 禁止直接编辑** → 一律 `hermes config set`。
- **OCI 公网 130.61.110.133 本地无法直连**（一切外网走隧道）→ 本机 Cursor 连 OCI 需 Cloudflare 隧道/SSH -L，不能直接填公网 IP。
- **Codex 报 `400 missing tags` 诊断树**（2026-08-30 实战）：报错体 `litellm.BadRequestError: ... Additional info: missing tags`。→ ① 根因 = litellm 把 `gpt-5.x` 别名转发到 **nous**（`inference-api.nousresearch.com`），nous 免费层强制 `tags` 字段，而 Codex 的 `/v1/responses` 调用不传 → 400。② 快速验证：`python3 -c "from openai import OpenAI; c=OpenAI(base_url='http://127.0.0.1:4100/v1',api_key='x'); print(c.chat.completions.create(model='gpt-5.2',messages=[{'role':'user','content':'hi'}],max_tokens=20).choices[0].message.content)"` 若报 missing tags 即确认。③ 修法 = 把 litellm_config.yaml 里所有 `gpt-5.2/gpt-5.1/gpt-5/gpt-4o` 别名改映射到 `openrouter/nvidia/nemotron-3.5-lightning:free`（或 `cohere/north-mini-code:free`），`api_key: os.environ/OPENROUTER_API_KEY`，**不要 api_base**。重启 litellm 后再测。④ 注意 litellm 是手动 `nohup`/`background` 起的，重启用 `pgrep -f "litellm --config"` 找 pid → `kill` → 重新起（禁用 nohup，terminal 用 `background=true`）。
- **litellm 网关非 systemd 托管**（2026-08-30 现状）：当前 4100 是手动 `background` 起的进程，机器重启会丢。换机/重启后若 Codex 连不上，先 `pgrep -f "litellm --config"` 看进程在不在，不在就按上面重启。**TODO**：应做成 `codex-free-proxy.service`（systemd `WantedBy=default.target` + `Restart=always`）开机自启，避免每次手动拉。

## references/
- `references/codex.config.toml.example`：Codex 免登录 TUI 配置模板（自定义 litellm provider）。
- `references/cursor.settings.json.example`：Cursor free_poll provider 指向 litellm 网关模板。
- `references/codex-free-models.md`：Codex 走免费模型完整落地（旧版细节，已并入本 SKILL 主文档，保留备查）。
- `references/client-config-cc-cursor.md`：CC/Cursor 客户端配置旧版（已过时，以本 SKILL 为准）。
- `references/openrouter-free-models.md`：OpenRouter 免费模型实测清单 + 整层全挂坑。
- `scripts/`：litellm_config.yaml / start_litellm.sh / codex_tool_filter.py / codex-free-proxy.service / codex-tool-filter.service / free_model_watchdog.sh / daily_free_model_research.sh / azure_spend_guard.sh
