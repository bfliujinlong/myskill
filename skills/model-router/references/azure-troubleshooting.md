# Azure 模型调优参考

## GPT-5-mini 部署限制（2026-09-08 实测）

| 参数 | 正确值 | 错误值 | 后果 |
|---|---|---|---|
| token 参数 | `max_completion_tokens` | `max_tokens` | 400 Bad Request |
| temperature | 默认 1 | 0.0~0.9 | 429 Rate Limited |
| api-version | 2025-04-01-preview | 2024-02-15-preview | 404 Not Found |
| reasoning_tokens | 60%+ 被烧掉 | - | content 为空 |

## 调试清单

1. 确认 key 位于 `AZURE_FOUNDRY_API_KEY` 环境变量
2. 用以下命令测试连接：
```bash
curl -X POST "https://liujl-9958-resource.openai.azure.com/openai/deployments/gpt-5-mini/chat/completions?api-version=2025-04-01-preview" \
  -H "api-key: $AZURE_FOUNDRY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hello"}],"max_completion_tokens": 8000}'
```

3. 预期返回：有 `choices[].message.content`
4. 若返回空：加大 `max_completion_tokens` 或改用 `gpt-4o-mini`

## 替代方案

如果 GPT-5-mini 持续返回空，改用：
- `gpt-4o-mini`（更可靠，content 完整）
- `qwen-plus`（阿里云，需阿里云 key）

---
## 新增：Azure Foundry Key 401 失效修复（2026-09-18）

**症状**：Azure OpenAI 端点（`https://liujl-9958-resource.openai.azure.com/openai/deployments/gpt-5-mini/chat/completions`）返回 401 `Access denied due to invalid subscription key`。
**根因**：Azure Sponsorship $5000 额度耗尽后，资源自动转为 PAYG 模式，订阅未配置计费方式，导致所有请求 401。
**修复方法**：
1. 登录 Azure Portal → 确认订阅状态和计费配置
2. 如果额度耗尽，重新申请 Sponsorship 或切换到备用 Azure 资源
3. 确认 `api-version=2025-04-01-preview` 仍有效
4. 重新配置 `.env` 中的 `AZURE_FOUNDRY_API_KEY`

**注意**：Azure Foundry 部署的 `gpt-5-mini` 默认将 90%+ token 烧在 `reasoning_tokens` 上，导致 `content` 为空。解决方法：
- 传递 `reasoning_effort: "none"`（如果部署支持）
- 增加 `max_completion_tokens` 到 8000+
- 改用 `gpt-4o-mini` 代替（没有 reasoning 问题）

---
## 新增：Palantir Foundry MCP 配置（2026-09-18 安装）

**安装**：`npm install -g palantir-mcp@0.14.0`
**配置格式**（Claude Code 项目级 MCP）：
```json
{
  "mcpServers": {
    "palantir-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "palantir-mcp", "--foundry-api-url", "https://<your-hostname>"],
      "env": {"FOUNDRY_TOKEN": "<token>"},
      "disabled": false
    }
  }
}
```
**安全数据流模型**（根据 Palantir 文档）：
- 数据流向第三方 LLM 提供商（Anthropic/Microsoft）
- 数据治理取决于与提供商的合同关系，非 Palantir 控制
- 所有写入操作（Ontology 修改）需要人工审批才能合并到主本体
- `deepseek-chat`（DeepSeek API，需 key）