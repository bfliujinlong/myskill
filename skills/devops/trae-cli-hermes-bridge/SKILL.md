---
name: trae-cli-hermes-bridge
description: Use when 把 TRAE CLI 模型接入 Hermes /model 选择器。
---

# TRAE CLI → Hermes 接入

## 背景

TRAe CLI (`traecli`) 只暴露 websocket/stdio（`app-server`、`exec-server`），**没有** OpenAI 兼容 HTTP 接口，不能直接填进 Hermes 的 `providers`。必须套一层 shim。

方案与本机 `cb2openai.py`（CodeBuddy→Hermes，:4100）同构。

## 架构

```
Hermes → http://127.0.0.1:4200/v1/chat/completions
       → trae2openai.py (FastAPI)
       → subprocess: traecli exec -y -c 'model="真名"' <prompt>
       → 复用 ~/.trae/cli/auth.json 的 OAuth 会话（无需 API Key）
```

## 关键实现（照抄 cb2openai.py 结构）

文件：`/home/ubuntu/.hermes/deploy/trae2openai.py`，端口 **4200**。

### 1. 模型别名映射（必做）

traecli 真实模型名带空格和中文（`DeepSeek-V4-Pro 正式版`），Hermes/litellm 传参不便。必须用短别名暴露：

```python
ALIASES = {
    "trae-ds4p": "DeepSeek-V4-Pro 正式版",
    "trae-glm53": "GLM-5.3",
    ...
}
```

### 2. 单次模型覆盖用 `-c`

```bash
traecli exec -y -c 'model="MiniMax-M3"' "prompt"
```

✅ 实测生效。比改 toml 默认值更可靠（不污染源配置）。

### 3. 环境必须最小化

```python
env = {"HOME":..., "PATH":"/home/ubuntu/.local/bin:/usr/bin:/bin", "TERM":"dumb"}
```

不清理会继承 Hermes 的污染变量导致 CLI 失败。

### 4. 输出要剥噪声

`traecli exec` 输出混了 ANSI 转义 + 状态行（`model:` / `provider:` / `tokens used`）。`_extract()` 逐行过滤这些前缀。

## systemd 坑（踩过）

❌ `ExecStart=/usr/bin/python3 trae2openai.py` → 卡 activating，无日志
原因：`/usr/bin/python3` **没有 uvicorn**（只有 fastapi）。

✅ 用 hermes-install venv 的 python + uvicorn 模块方式：

```ini
Environment="PATH=/home/ubuntu/.hermes/hermes-install/venv/bin:/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/ubuntu/.hermes/hermes-install/venv/bin/python -m uvicorn trae2openai:app --host 127.0.0.1 --port 4200
```

## config.yaml 注册（两处都要写）

只写顶层 `providers` 不会出现在 `/model`；必须同时写 `model.providers`：

```yaml
providers:
  trae:
    api_key: dummy
    base_url: http://127.0.0.1:4200/v1
    models:
      "trae-ds4p": ...

model:
  providers:
    trae:
      context_length: 131072
      models:
        trae-ds4p: ...
```

改前先备份：`cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak-$(date +%Y%m%d-%H%M%S)`

## Gateway 重启（红线）

在 gateway 进程树内 `systemctl --user restart hermes-gateway` 会被拦截（SIGTERM 传播）。

✅ 写脚本 + terminal background 模式：

```bash
cat > /tmp/restart_gw.sh <<'EOF'
#!/bin/bash
sleep 2
systemctl --user restart hermes-gateway.service
EOF
chmod +x /tmp/restart_gw.sh
```

然后 `terminal(command="/tmp/restart_gw.sh", background=true)`。

## 验证（必须实测，不能只看配置）

```bash
# 1. 服务
curl -s http://127.0.0.1:4200/v1/models | python3 -c "import sys,json;print(len(json.load(sys.stdin)['data']))"

# 2. 端到端（这才是标准）
hermes -z "只回复四个字: 链路通了" -m "trae/trae-glm53"
```

## 已知限制

- 只取纯文本回答，**不支持原生 function calling** → Hermes 工具调用在此 provider 上退化为普通问答
- `traecli` 单次调用约 15-60s（含 CLI 冷启动），比原生 API 慢
- 依赖 `~/.trae/cli/auth.json` 的 OAuth 会话，过期后需重新登录

## traecli 配置坑

`model` 必须写在 `~/.trae/traecli.toml` **最顶部**。放在 `[projects.xxx]` 下会被解析成项目字段，报 `projects.xxx.model is ignored`。

`approval_policy` / `sandbox_mode` 同理会被忽略，真正生效的是命令行 `-y`。

配套切换脚本 `~/.local/bin/trae-model`（`trae-model` 列、`trae-model 10` 切、`trae-model current` 查）。
