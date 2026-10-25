---
name: pi-agent
description: Use Pi Agent (OpenRouter coding assistant) for code analysis, generation, and review. Trigger when user says "使用 pi" / "pi 分析" / "pi 审查" / "pi 写" / "用 pi".
version: 1.0.0
---

# Pi Agent

OpenRouter 官方 coding agent，支持代码分析、生成、审查。

## 触发条件

用户消息包含以下关键词时激活：
- "使用 pi"
- "pi 分析"
- "pi 审查"
- "pi 写"
- "用 pi"
- "pi agent"

## 执行方式

### 单次调用（推荐）

```bash
# 分析文件
pi -p "分析这段代码的安全漏洞" @src/auth.ts

# 审查代码
pi -p "Review this PR for performance issues" @src/api/handlers.ts

# 生成代码
pi -p "写一个 React 组件，带表单验证" @src/components/Form.tsx

# 纯文本问答
pi -p "解释什么是 zero-knowledge proof"
```

### 多文件分析

```bash
pi -p "分析这个项目的架构" @src/index.ts @src/routes/ @src/models/
```

### 指定模型

```bash
# 使用免费模型（默认）
pi --model "nvidia/nemotron-3-super-120b-a12b:free" -p "..."

# 使用付费模型（需余额）
pi --model "anthropic/claude-sonnet-4" -p "..."
pi --model "google/gemma-3-27b-it:free" -p "..."
```

## 配置

- **配置文件**: `~/.pi/agent/settings.json`
- **认证**: `~/.pi/agent/auth.json` (OpenRouter API key)
- **默认模型**: `nvidia/nemotron-3-super-120b-a12b:free`
- **默认 Provider**: OpenRouter

## Hermes 集成示例

**用户**: "用 pi 分析 lilly iac 代码"

**Hermes 执行**:
```bash
pi -p "分析这个项目的 IaC 架构，指出潜在问题和优化建议" @/home/ubuntu/lilly/terraform/
```

**用户**: "pi 审查这个 PR"

**Hermes 执行**:
```bash
pi -p "Review this code for security vulnerabilities, performance issues, and best practices" @src/api/
```

## 交互模式（不推荐用于 Hermes）

Pi 有交互式 TUI，但 Hermes 应使用 `-p` 单次调用模式，避免阻塞。

```bash
pi  # 进入交互模式（仅用于调试）
```

## 可用模型

### 免费模型（OpenRouter，2026-10 大面积退场）
- `qwen/qwen3-coder:free` — 未测，可能存活
- `qwen/qwen3-next-80b-a3b-instruct:free` — 未测
- `tencent/hy3-preview:free` — 列表在，待验证

**已死（勿再用）**：
- ❌ `nvidia/nemotron-3-super-120b-a12b:free` — 404 "unavailable for free"
- ❌ `google/gemma-3-27b-it:free` — 429 限流
- ❌ `thinkingmachines/inkling:free` — 404
- ❌ `nvidia/nemotron-3-nano-30b-a3b:free` — 404 转付费
- ❌ `openrouter/free` — 404

### 付费模型
- `anthropic/claude-sonnet-4` — Claude 最新
- `openai/gpt-4o` — GPT-4o
- `google/gemini-pro-1.5` — Gemini Pro

## 免费模型全挂时的降级策略

Pi Agent 只支持 OpenRouter provider，当 OR 免费池全灭时：
1. 用 `--model` 指定可能存活的模型（上面"未测"列表）
2. 若全部失败，降级到 `web_search` + 本模型直接回答（0 token 消耗）
3. 报告用户 Pi Agent 不可用，说明根因（OR 免费池退场）
4. 不要反复换模型重试（浪费 API 调用），一轮探测 3-4 个后放弃

## 错误处理

1. **API key 无效**: 检查 `~/.pi/agent/auth.json`
2. **模型不存在**: 用 `--model` 切换到可用模型
3. **超时**: 大文件分析可能超时，拆分文件或换小模型

## 相关命令

```bash
# 查看 Pi 版本
pi --version

# 查看帮助
pi --help

# 列出已安装扩展
pi list

# 更新 Pi
pi update
```
