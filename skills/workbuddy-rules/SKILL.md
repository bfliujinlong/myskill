---
name: workbuddy-rules
description: "WorkBuddy 全局公约与四类规则：云迁移交付规范（AC-MIG 定价/SOW 14 章）、编码规范（三层架构/AI 四段式）、售前报价规范（双语/去AI味）、输出风格。涉及报价、SOW、方案文档、代码规范、交付物格式时触发。"
version: 1.0.0
author: jinlongliu
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [云迁移, AC-MIG, 报价, SOW, 全局公约]
    related_skills: [cloud-migration-pm, qy-dubaifintech-bid, aiccp-platform, pcs-presales-ps]
---

# When to Use
- 写报价 / SOW / HLD / LLD / 任何对外交付文档
- 编写或评审代码（尤其 AICCP 平台）
- 需要确认定价口径（AC-MIG / $350人天）或文档格式时

# 细则索引（按需展开 references/）
| 文件 | 内容 |
|---|---|
| `references/global-convention.md` | 全局公约：身份、在办项目台账、不可违反的边界 |
| `references/cloud-msp.md` | 迁移五阶段、LZ 八领域、AC-MIG 定价、SOW 14 章、数字口径 |
| `references/coding.md` | 技术栈、三层架构、UUID 主键、RBAC、AI 四段式调用 |
| `references/selling.md` | 报价结构、中英双语分文件、去 AI 味清单、客户沟通 |
| `references/output-style.md` | 语言、结构、状态符号、交付物格式、工作习惯 |
| `references/codebuddy-auth-bridge.md` | CodeBuddy(auth提取/桥接/隧道/CF UI更新)步骤与坑 |

# 硬边界（速记）
- 凭证只写本地文件不进对话；不编造数字（未核实就标注）；AI 能力必须走 Skill → Prompt → LLM → Structured Output；外部动作先确认，内部动作直接做；核心问题未解决不中断。
- **交互风格（用户强制要求，已固化）：简洁直接，先推断上下文再回答，不反问确认；无长闭合循环（禁止"已执行全部清理...已完成"式自嗨）；技术断言先用工具验证（curl/grep/file）再说，不凭记忆；遇到阻塞先试 A/B/C 再求助，求助时带已试现象；敏感凭证 `chmod 600`，不粘贴到对话；用户说"已足够"/"切"/"修"/"直接说"时立即执行，不再列步骤确认。**
- **模型路由验证：切换默认模型前必须 `curl` 实测目标端点（如 Free Model / Azure / CF Workers AI），确认 `HTTP 200`+有效内容，再改 `hermes config`；禁止凭记忆假设模型可用。**
