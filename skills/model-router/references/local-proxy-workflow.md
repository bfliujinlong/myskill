# 本地代理 + 公网暴露工作流

## 场景一：笔记本企业模型暴露

用户笔记本（Windows）开着 Trae CLI / WorkBuddy（企业付费 Credits），需要让远程的 Hermes Agent 调用这些能力。

### 方案：笔记本代理 + 公网暴露

```
Hermes (OCI) → 公网地址 (trycloudflare.com) → laptop_proxy.py (笔记本) → Trae/WorkBuddy 本地端口
```

### 步骤

#### 1. 笔记本端
```powershell
# 确认实际监听端口
netstat -ano | findstr LISTENING | findstr :5001
netstat -ano | findstr LISTENING | findstr :5002

# 启动代理（默认 Trae=5001, WB=5002，按需修改环境变量）
$env:TRAE_LOCAL="http://127.0.0.1:50010"  # 如果实际端口不同
python laptop_proxy.py

# 另开一个 PowerShell 窗口暴露公网
cloudflared tunnel --url http://localhost:3000
```

#### 2. 远程调用
```bash
curl -X POST https://xxxx.trycloudflare.com/trae/chat \
  -H 'Content-Type: application/json' \
  -d '{"model":"trae","messages":[{"role":"user","content":"你好"}]}'
```

### 备选暴露方式（无需下载）

#### Serveo SSH 隧道
```powershell
ssh -R 80:localhost:3000 serveo.net
# 输出 https://randomname.serveo.net
```

#### ngrok
```powershell
ngrok http 3000
```

### Windows 防火墙
```powershell
netsh advfirewall firewall add rule name="Trae" dir=in action=allow protocol=TCP localport=<端口>
```

---

## 场景二：Claude Code 多模型代理（LiteLLM，端口 4000）

### 场景

本机 Claude Code CLI 需要同时使用 **Claude 免费**（OpenRouter）和 **Qwen**（阿里云百炼），不能只绑死一个 provider。

### 架构

```
Claude Code CLI → localhost:4000 (LiteLLM) → OpenRouter (Claude Sonnet free)
                                            → DashScope (Qwen 3.8 max)
```

### 1. LiteLLM 配置文件

写入 `~/.litellm/config.yaml`。

**⚠️ OpenRouter 免费 Claude 模型已于 2026-10 全部下架**（`anthropic/claude-sonnet-4.5:free` 等返回 404），所有 Claude 模型名一律路由到 Qwen token-plan。

**⚠️ Claude Code 会发送多种模型名**（`claude-sonnet-4-20250514` / `claude-sonnet-5-5` / `claude-opus-5-5`），config 里必须**每个变体都注册**，否则报 `Invalid model name passed in model=xxx`。

```yaml
model_list:
  # Claude Sonnet 系列 → 一律路由到 Qwen
  - model_name: claude-sonnet-4-20250514
    litellm_params:
      model: openai/qwen3.8-max
      api_base: https://token-plan.cn-beijing.maas.aliyuncs.com/v1
      api_key: os.environ/DASHSCOPE_API_KEY
      timeout: 120
      max_tokens: 4096

  - model_name: claude-sonnet-5-5
    litellm_params:
      model: openai/qwen3.8-max
      api_base: https://token-plan.cn-beijing.maas.aliyuncs.com/v1
      api_key: os.environ/DASHSCOPE_API_KEY
      timeout: 120
      max_tokens: 4096

  # Claude Opus 系列 → 一律路由到 Qwen
  - model_name: claude-opus-5-5
    litellm_params:
      model: openai/qwen3.8-max
      api_base: https://token-plan.cn-beijing.maas.aliyuncs.com/v1
      api_key: os.environ/DASHSCOPE_API_KEY
      timeout: 120
      max_tokens: 4096

  # 直接调用 Qwen（如显式指定）
  - model_name: qwen3.8-max
    litellm_params:
      model: openai/qwen3.8-max
      api_base: https://token-plan.cn-beijing.maas.aliyuncs.com/v1
      api_key: os.environ/DASHSCOPE_API_KEY
      timeout: 120
      max_tokens: 4096

router_settings:
  routing_strategy: simple-shuffle
  num_retries: 2
  retry_after: 5

general_settings:
  port: 4000
  master_key: sk-ant-local
```

### 2. Claude Code settings.json

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_API_KEY": "***"
  },
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)"],
    "deny": []
  }
}
```

### 3. keys.env（API 密钥，chmod 600）

写入 `~/.litellm/keys.env`：
```
OPENROUTER_API_KEY=<实际 key>
DASHSCOPE_API_KEY=<实际 key>
```

### 4. 启动与验证

```bash
# 杀旧进程
kill $(lsof -ti:4000) 2>/dev/null; sleep 1

# 启动
source ~/.litellm/keys.env
source ~/.hermes/hermes-install/venv/bin/activate
nohup litellm --config ~/.litellm/config.yaml --port 4000 > ~/.litellm/litellm.log 2>&1 &

# 验证
sleep 3
ss -tlnp | grep 4000
curl -sS http://localhost:4000/health
```

### 5. systemd service（持久化）

写入 `~/.config/systemd/user/litellm-proxy.service`：

```ini
[Unit]
Description=LiteLLM Proxy - Qwen router for Claude Code
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu/.litellm
EnvironmentFile=/home/ubuntu/.litellm/keys.env
ExecStart=/data/hermes-install/venv/bin/litellm --config /home/ubuntu/.litellm/config.yaml --port 4000
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

**⚠️ 坑：环境变量不加载**：
- `EnvironmentFile` 必须用**绝对路径**（`~/` 不展开）
- 编辑 service 文件后必须 `systemctl --user daemon-reload` 再 `restart`，否则 systemd 用旧的 unit 定义
- 验证环境变量是否加载到进程：`cat /proc/$(pgrep -f litellm)/environ | tr '\0' '\n' | grep DASHSCOPE`，无输出说明 env 没加载
- `keys.env` 里的值不能是 `***`（工具脱敏导致）——用 `python3 -c` 读取真实 key 再 `>>` 追加，不要用 `write_file` / `execute_code` 写密钥（它们会把值替换成 `***`）

### 已知坑

- **`alternatives` 字段不被支持**：Claude Code settings.json 不支持 `alternatives` 数组做模型切换，写了被忽略或报错
- **cc2azure vs LiteLLM**：cc2azure 只能代理 Azure gpt-5-mini；LiteLLM 支持多 provider 通用路由
- **master_key**：`sk-ant-local` 是假 key（Claude Code 必须设非空 API_KEY），不做真实鉴权
- **OpenRouter HTTP/2**：从 OCI 用 curl 调 OpenRouter 会 HTTP/2 握手失败，LiteLLM 内部用 httpx（http2=False）绕过
- **keys.env 安全**：必须 `chmod 600`，含真实 API keys
- **端口冲突**：必须先 `systemctl --user stop cc2azure.service && systemctl --user disable cc2azure.service`（不能只 kill 进程，systemd 会自动拉起）再启 LiteLLM
- **terminal background + source**：`terminal(background=True)` 不支持 shell 内置命令 `source`，用 `bash -c 'source ... && cmd'` 或绝对路径
- **config.yaml 密钥脱敏**：`execute_code` / `write_file` / `terminal` 工具会把密钥值替换成 `***...`，导致 LiteLLM 解析 YAML 失败。必须用 `os.environ/KEY_NAME` 引用，不要在 config.yaml 里写任何密钥字面量
- **Claude Code 模型名变体**：用户通过 `/model` 切换时会发送 `claude-opus-5-5` / `claude-sonnet-5-5` 等名，config 里没注册的模型名直接返回 400 `Invalid model name`。每个可能被请求的名字都要加 `model_name` 条目
- **OpenRouter 免费 Claude 已下架**（2026-10）：`anthropic/claude-sonnet-4.5:free` 等全返回 404，不要再配。所有 Claude 模型名一律路由到 Qwen
- **外网端口不通**：OCI 安全组/iptables 可能没开 4000 端口。如果 Claude Code 在笔记本上连不上，检查 `iptables -L INPUT -n | grep 4000` 和 Oracle Cloud 安全组规则

---

## 已知坑（笔记本代理）

1. **端口不对**：Trae CLI 默认可能是 50010/50018 而非 5001，用 netstat 确认
2. **WorkBuddy 无本地端口**：可能是纯客户端，走云端 API，无法通过本地代理中转
3. **cloudflared 下错版本**：注意 `cloudflared-darwin-amd64` 是 macOS 版，Windows 要下 `cloudflared-windows-amd64.exe`
4. **GitHub 被墙**：下载失败时用 Serveo SSH 隧道替代
5. **502 错误**：公网通了但目标服务没连上，检查端口/防火墙
6. **环境变量**：PowerShell 用 `$env:XXX="value"`，不是 `export XXX=value`

---

## 场景三：OpenRouter Agent SDK 与 Agentic 模型

### 场景

调用 OpenRouter 上的 Agentic 模型（如 `thinkingmachines/inkling:free`），这些模型要求专用 Agent harness，标准 chat API 会被拒绝（报 `This model requires an agentic harness`）。

### Python SDK（非标准 API）

```bash
source /data/hermes-install/venv/bin/activate
pip install openrouter-agent-sdk
```

**⚠️ API 不是 OpenAI 兼容格式**——没有 `client.chat.completions.create()`，只有 `client.chat.send()`：
```python
from openrouter import OpenRouter
import os

client = OpenRouter(api_key=os.environ['OPENROUTER_API_KEY'])
result = client.chat.send(
    model="thinkingmachines/inkling:free",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=500
)
```

**坑**：
- `Chat` 对象没有 `completions` 属性，用 `dir(client.chat)` 确认实际方法
- 部分免费模型返回 `This model requires an agentic harness` → 必须用 TypeScript SDK 或 Pi Agent
- `nemotron-3-super-120b:free` 等推理模型会把几乎所有 token 烧在 `reasoning_tokens` 上，`max_tokens` 设小会空回复

### TypeScript SDK（推荐）

```bash
npm install @openrouter/agent @openrouter/sdk
```

```javascript
import { callModel } from "@openrouter/agent";
const result = await callModel({
  model: "thinkingmachines/inkling:free",
  input: [{ role: "user", content: "Hello" }],  // input 不是 messages
  maxTokens: 500,
  apiKey: process.env.OPENROUTER_API_KEY,
  tools: [],  // agentic 模型可能强制要求此字段
});
```

**坑**：
- 参数是 `input` 不是 `messages`
- 导出的是 `callModel` 不是 `Agent`
- 不传 `tools` 会报 `Cannot destructure property 'tools' of 'request'`

### Pi Agent（编码 Agent CLI）

```bash
npm install -g @mariozechner/pi-coding-agent
```

配置 `~/.pi/agent/auth.json`（OpenRouter key）+ `~/.pi/agent/settings.json`（defaultProvider=defaultModel）。用法：`pi --print "prompt"` 非交互，`pi` 交互 TUI。

**定位**：独立的编码 Agent（有 read/bash/edit/write 工具），适合交互式代码分析，不适合 programmatic 调用。

### Codex CLI（ARM64 永久不可用）

`@openai/codex` npm 包缺 `@openai/codex-linux-arm64`，`npm install -g` 直接报 `Missing binary`。不要尝试强制安装。

**降级规则**：用户说「使用 Codex」→ 自动降级 Azure `gpt-4o`（`provider=azure-foundry`），禁止反弹「你没装」。
