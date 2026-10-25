# Codex CLI 走免费模型（litellm 网关 + tool-filter 代理）

## 适用场景
Codex CLI（`@openai/codex`，0.149.x）默认连 OpenAI 官方/ChatGPT 账号。要接免费模型（nous/OR）必须绕开它的两条硬约束（见正文坑段）。本文件是**已验证 EXIT=0** 的完整落地。

## 架构
```
Codex CLI
  └─ openai_base_url=http://127.0.0.1:4101/v1   (model="hy3")
       └─ codex-tool-filter  (:4101, 极简 Python 反向代理)
            ├─ 清空所有 tools 字段 (Codex 本地自跑工具, 模型只需文本/代码)
            ├─ WS 升级请求 → 403 (逼 Codex 降级 HTTPS)
            └─ 转发 → litellm  (:4100)
                          └─ 多 deployment 同 model_name="hy3" 轮询
                               ├─ nous: hy3/solar/laguna/stepfun/longcat (免费)
                               └─ azure-gpt5mini (兜底, 需 reasoning_effort:low)
```

## 1. 安装 litellm（独立 venv，不污染 hermes venv）
```bash
python3 -m venv /home/ubuntu/.litellm-venv
source /home/ubuntu/.litellm-venv/bin/activate
pip install "litellm[proxy]"   # 含 websockets, 支持 /v1/responses WS+HTTP
deactivate
```

## 2. litellm 配置（deploy/litellm_config.yaml）
**不要用 `router_settings.fallbacks`**（1.98 格式极坑，报 not a dictionary）。用**同一 model_name 多个 deployment** 让 litellm 自动轮询：
```yaml
general_settings:
  allow_requests_without_auth: true
  telemetry: false

model_list:
  - model_name: hy3
    litellm_params:
      model: openai/tencent/hy3:free
      api_base: https://inference-api.nousresearch.com/v1
      api_key: os.environ/NOUS_API_KEY
  - model_name: hy3
    litellm_params:
      model: openai/upstage/solar-pro4:free
      api_base: https://inference-api.nousresearch.com/v1
      api_key: os.environ/NOUS_API_KEY
  - model_name: hy3
    litellm_params:
      model: openai/poolside/laguna-s-2.1:free
      api_base: https://inference-api.nousresearch.com/v1
      api_key: os.environ/NOUS_API_KEY
  - model_name: hy3
    litellm_params:
      model: openai/stepfun/step-3.7-flash:free
      api_base: https://inference-api.nousresearch.com/v1
      api_key: os.environ/NOUS_API_KEY
  - model_name: hy3
    litellm_params:
      model: openai/meituan/longcat-2.0:free
      api_base: https://inference-api.nousresearch.com/v1
      api_key: os.environ/NOUS_API_KEY
  # Azure 兜底 (难任务显式 model=azure-gpt5mini 时走这)
  - model_name: azure-gpt5mini
    litellm_params:
      model: azure/gpt-5-mini
      api_base: https://liujl-9958-resource.openai.azure.com/
      api_version: 2025-04-01-preview
      api_key: os.environ/AZURE_OPENAI_API_KEY
      deployment_name: gpt-5-mini
      reasoning_effort: low   # 否则 Azure 烧光 token 限流 429

router_settings:
  num_retries: 3
  timeout: 60
  retry_policy: {"Retry-After": 1}
```
⚠️ OR 免费池已转付费（`nvidia/nemotron-3-nano-30b-a3b:free` 实测 `This model is unavailable for free`）→ 不进免费主链。

## 3. litellm 启动脚本（deploy/start_litellm.sh）
```bash
#!/bin/bash
cd ~/.hermes
source /home/ubuntu/.hermes/.env 2>/dev/null
source /home/ubuntu/.litellm-venv/bin/activate
exec litellm --config /home/ubuntu/.hermes/deploy/litellm_config.yaml --port 4100 --host 127.0.0.1
```
`chmod +x`。systemd unit `codex-free-proxy.service` 用 `EnvironmentFile=/home/ubuntu/.hermes/.env` + `ExecStart=/home/ubuntu/.hermes/deploy/start_litellm.sh`。

## 4. tool-filter 代理（deploy/codex_tool_filter.py）
剥 namespace tool + 对 WS 返回 403。**必须 `allow_reuse_address=True`**（否则 systemd 重启风暴占端口）。
```python
# 见 SKILL 正文或直接复制本仓库 scripts/codex_tool_filter.py
```
要点：`UPSTREAM="http://127.0.0.1:4100"`；`ALLOWED={"function","web_search","x_search"}`；`do_POST` 只处理 `responses`/`chat/completions`，其他 404；继承 `ReuseTCPServer(allow_reuse_address=True)`。

## 5. systemd units
`~/.config/systemd/user/codex-free-proxy.service`（litellm）和 `codex-tool-filter.service`（filter，After=codex-free-proxy.service）。两者 `Restart=always` + `RestartSec=5`。
```bash
systemctl --user daemon-reload
systemctl --user restart codex-free-proxy.service codex-tool-filter.service
# 若 filter 报 Address already in use: systemctl stop + reset-failed 再 start
```

## 6. Codex config（~/.codex/config.toml）
```toml
openai_base_url = "http://127.0.0.1:4101/v1"
model = "hy3"
[projects."/home/ubuntu"]
trust_level = "trusted"
```
⚠️ 删掉 `~/.codex/auth.json`（若有 ChatGPT 登录态会干扰，Codex 优先用 auth.json 的官方端点）。

## 7. 验证
```bash
# litellm 起来
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4100/v1/models   # 期望 200
# filter 起来 + 剥离 namespace 生效
curl -s -X POST http://127.0.0.1:4101/v1/responses -H "Content-Type: application/json" \
  -d '{"model":"hy3","input":"用中文回四个字:配置成功","tools":[{"type":"namespace","name":"x"}]}' \
  --max-time 40 | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['output'][0]['content'][0]['text'])"  # 期望 "配置成功"
# Codex 端到端
codex exec -m "hy3" "用中文回复四个字：配置成功"   # 期望输出 配置成功, EXIT=0
```
⚠️ Codex 日志里会刷一堆 `ws://... 403` / `Falling back from WebSockets to HTTPS transport` —— **这是正常的**，它先试 WS（被 filter 拒），降级 HTTPS 后成功。

## 关键坑（本会话踩过）
- litellm `router_settings.fallbacks` 三种写法（`["a","b"]` / `- - a - b` / `dict 映射）全报 `not a dictionary` → 用同 model_name 多 deployment。
- litellm `proxy_hooks` 的 `request_hook` / `response_api_request_hook` **对 /v1/responses 不调用** → namespace 过滤必须用外部 filter 代理，别在 litellm 里折腾 hook。
- Codex `disabled_tools` / `CODEX_DISABLE_WEBSOCKETS` 环境变量**不生效**。
- filter 脚本若没 `allow_reuse_address=True` + systemd `Restart=always` → 端口抢占死循环（`Address already in use`）。
- Azure gpt-5-mini 作 Codex 默认后端会 429（限流 + reasoning 烧光）→ Codex 默认用 nous 池（`model="hy3"`），Azure 仅显式兜底。
