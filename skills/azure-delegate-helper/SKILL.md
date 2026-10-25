---
name: azure-delegate-helper
description: "处理 '用openai'/'难任务' 请求：delegate 给 Azure GPT-5-mini 时的配置和调试指南"
version: "0.1.0"
author: "Hermes Agent"
license: "MIT"
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [azure, openai, gpt-5, 委托任务, 费用控制]
---

# Azure Delegate Helper

当用户说 **"用openai"** 或 **"难任务"** 时，使用此技能 delegate 给 Azure GPT-5-mini。

## 触发条件

- 用户消息包含："用openai"、"用gpt5"、"难任务"、"切付费"
- 任务需要深度分析、架构设计、复杂逻辑推理
- 自动化流程、售前方案、迁移方案等

## 委托模板

```python
delegate_task(
  tasks=[{
    "goal": "完成用户指定的困难任务",
    "context": f"用户需求：{user_request}\n\n关键约束：{constraints}\n\n参考资料：{files}\n\n请输出完整解决方案，注意：Azure GPT-5-mini 会烧大量 token 做 reasoning，实际返回的 content 可能会较少，需要你根据 reasoning 字段组织连贯答案。",
    "output_schema": {"type": "object"}
  }],
  action="spawn",
  model="gpt-5-mini",
  provider="azure-foundry"
)
```

## 关键参数注意事项

### Azure OpenAI 参数坑

| 参数 | 用法 | 说明 |
|---|---|---|
| `max_completion_tokens` | 必填 8000+ | 不填会 400 错误 |
| `temperature` | 不能为空 | 传 1.0 或不传，默认值 |
| `api-version` | 2025-04-01-preview | 旧版 404 |
| `reasoning_tokens` | 由服务自动烧 | content 可能为空 |

### delegate_task 使用

```python
# 正确姿托
delegate_task(
  action="spawn",
  model="gpt-5-mini",
  provider="azure-foundry",
  context="...",
  goal="完成任务并返回结果"
)

# 错误委托（别这么做）
# model="gpt-5"  # 名字不匹配
# provider="openai"  # 不是 azure-foundry
# temperature=0.3  # 传这个会 429
```

## 费用监控

Azure GPT-5-mini 计费模型：
- **token 计费**：按实际消耗的 token 计算
- **reasoning token**：计费但不返回 content
- **estimated_cost = (prompt_tokens + completion_tokens) * $0.0001**

### 手动记账
每次 delegate 后在 `azure_spend_guard.sh` 里记账：
```bash
./azure_spend_guard.sh record "gpt-5-mini reasoning_tokens=1500"
```

## 回退方案

如果 Azure 调用失败：
1. 检查 `AZURE_FOUNDRY_API_KEY` 是否有效
2. 回退到 `poolside/laguna-s-2.1:free` 或 `meituan/longcat-2.0:free`
3. 告知用户："付费通道暂不可用，已用免费模型处理"

## 常见问题

**Q：为什么回传的结果很短？**
A：GPT-5-mini 默认烧 80% token 做 reasoning。确保在 delegate 时 `max_completion_tokens` 很大（如 8000）。

**Q：我该不会 delegate_task 语法怎么办？**
A：把用户的完整需求复制粘贴到 `context` 字段，我来组织模板。

**Q：怎么知道 Azure 还剩多少额度？**
A：访问 https://portal.azure.com/#view/Microsoft_Azure_Health/AzureOpenAI/usageView --- 或者看 ~/.hermes/scripts/azure_spend_guard.sh