---
name: hermes-mobile-bridge
description: "iPhone/Android 用 Siri 或快捷指令把 Hermes 当语音/桌面 AI 助理：OCI 中转服务 + Cloudflare 隧道暴露 + iOS 快捷指令配方。解决国内直连 Telegram 被墙、Nous 免费 API 需 tags 等问题。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, ios]
metadata:
  hermes:
    tags: [hermes, 移动端, siri, 快捷指令, ios, cloudflare, 隧道, 语音助理, 零费用]
    related_skills: [hermes-config-portability, ai-cloud-hub]
---

# Hermes 移动端语音助理桥接（iOS Shortcuts / Siri → Hermes）

## When to Use

- 用户想用 iPhone（Siri 唤醒）或 Android 把 Hermes 当桌面/随身语音 AI 助理
- 用户说「用 Siri 直接问 Hermes」「手机快捷指令连 Hermes」「国内不用 VPN 直连」
- 需要把 Hermes 能力暴露到手机，但**不依赖 Telegram App 直连**（国内墙死）

## 已验证架构（2026-08-30 实战跑通）

```
iPhone 快捷指令
  └─ 听写文本 → POST https://<CF隧道URL>/relay/ask?q=问题
       ↓ (国内直连 Cloudflare 边缘，不经过 Telegram)
OCI 机器 cloudflared quick/命名隧道 → nginx:3080 → /relay/ → 127.0.0.1:8099
       ↓
hermes_relay.py (FastAPI :8099)
       └─ 调 OpenRouter 免费模型 (OpenAI 兼容) → 返回 {"answer":"..."}
       ↓
快捷指令「获取词典值: answer」→「朗读文本」
```

**为什么不用 Telegram 中转**：国内 iPhone 直连 `api.telegram.org` 超时（GFW），且快捷指令 HTTP 请求默认不走 App 代理。Telegram Bot API 轮询 `getUpdates` 在快捷指令里还会踩 JSON→词典转换报错（"Cannot convert Rich Text to Dictionary" / "No Key Provided"）。**直接走 CF 隧道到自己 OCI 的中转服务最稳。**

## 标准部署步骤

### 1. 中转服务（OCI 机器）

- 用 `venv` 的 python（`/home/ubuntu/.hermes/hermes-install/venv/bin/python3`）跑，它需要 fastapi/httpx/dotenv/uvicorn/openai（系统 python3 缺这些，且 PEP668 限制）
- 模型调 **OpenRouter**（`nemotron-3.5-lightning:free` 或 `cohere/north-mini-code:free` 实测免费可用），**不要**用 Nous 免费层（见坑）
- systemd 托管 `tg-relay.service`（Restart=always），ExecStart 用 venv python 绝对路径

### 2. 暴露到公网（CF 隧道）

- quick tunnel（`cloudflared tunnel --url http://127.0.0.1:3080`）已暴露 nginx:3080
- 在 nginx 配置 `server { listen 3080 }` 内加：
  ```nginx
  location /relay/ {
      proxy_pass http://127.0.0.1:8099/;
      proxy_http_version 1.1;
      proxy_set_header Host $host;
      proxy_read_timeout 60s;
  }
  ```
  ⚠️ location 必须插在 server 块最后一个 `}` **之前**，否则 nginx 报 "location directive is not allowed here"。用 python 在 `s.rfind("}")` 前插入最稳。
- 公网地址：`https://<quick-tunnel-url>/relay/ask?q=...`
- ⚠️ quick tunnel URL 重启会变。长期稳定需 eu.org 域名 + 命名隧道固定路由（DuckDNS 因非 CF zone 发不了证书，不可行）

### 3. iOS 快捷指令（仅 5 步）

```
① 听写文本        (语言: 中文(中国大陆))
② URL            → https://<隧道URL>/relay/ask?q=听写文本
③ 获取URL内容     (默认 GET)
④ 获取词典值      → answer   (单层! 不是 result.message.text)
⑤ 朗读文本        (读 ④的 answer)
```

- 命名指令「问我助理」→ 喊「嘿Siri，打开问我助理」触发（Siri 原生能打开任意指令，无需绑短语）
- iOS 18 的「添加到 Siri」在**指令自身详情页**（长按指令→详情），不在「自动化」列表、也不在「设置→Siri」
- 国内直连必须走 CF 隧道域名，**不能**直连 api.telegram.org

## 常见陷阱（实测）

1. **Telegram API 国内超时** → 改用 CF 隧道中转，彻底绕开。
2. **Nous 免费 API 报 "missing tags"/"missing user tag"** → Nous 免费层强制要求 `tags`+`user` 字段，裸 REST / openai SDK / litellm 都补不上（Hermes 自身的 nous provider 适配器才处理得了）。**直接用 OpenRouter 免费模型**（OpenAI 兼容、无此限制）。
3. **litellm 4100 调 `hy3` 报 missing tags** → 同上，litellm 转发 nous 时也缺 tag。OCI 机器海外能直连 OpenRouter，故中转服务直连 OpenRouter 最省事。
4. **OpenRouter 模型下架** → `nvidia/nemotron-3-nano-30b-a3b:free` 已转付费（404）。可用 `nvidia/nemotron-3.5-lightning:free`、`cohere/north-mini-code:free`。先用 `curl` 探一下再写死。
5. **快捷指令「获取词典值」报错** → 来源必须是上一步「获取URL内容」的 JSON 返回；中转服务返回 `{"answer":"..."}` 只需取 `answer` 一层。若来源显示「URL的内容」或富文本，说明前一步没接对。
6. **systemd 服务用错 python** → `/usr/bin/python3` 无 fastapi；必须用 Hermes venv 的 python 绝对路径作 ExecStart。
7. **PEP668 外部管理** → 系统 python3 `pip install` 被拒，加 `--break-system-packages`（仅 sandbox 机器可接受），或直接用 venv python。

## 安全

- 中转服务**不存 bot token**（绕开 Telegram），iPhone 快捷指令里也无 token，符合用户「别明文保存」红线
- 中继返回纯模型回答，不含 Hermes 记忆/技能上下文（若要更聪明，让中继调 Hermes 网关，但网关无 REST chat API，需另加）
- CF 隧道 URL 若公开，任何人可 POST 你的中继（免费模型，成本极低，但建议加简单校验/限频）

## 参考文件

- `templates/hermes_relay.py` — 可复用的 FastAPI 中继服务（OpenRouter 免费模型）
- `templates/tg-relay.service` — systemd unit（venv python 绝对路径）
- `references/cf-nginx-relay.md` — nginx location 插入片段 + 验证命令
