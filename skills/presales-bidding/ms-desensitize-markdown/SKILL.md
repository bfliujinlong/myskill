---
name: ms-desensitize-markdown
description: 对 Markdown (.md) 文件执行脱敏处理。将真实客户标识（客户名、IP、主机名、域名、账号、凭据）替换为代号或 [REDACTED]，同时保留 SLA 数值、指标结构、排除条款等业务信息。适用于将 L2 原始材料脱敏后移入 L1 的场景。
---

# Markdown 脱敏 Skill

## 概述

对 Markdown 文件执行脱敏处理，将 L2 原始材料转化为 L1 可自动加载的脱敏版本。

**核心原则**：脱敏标识符，保留信息。

## 前置检查

1. 确认源文件位于 L2 区（06-项目材料-受限 或 03-Bidding场景素材/原始Sample）
2. 确认目标目录为 L1 区（04-脱敏案例库 或 02-Offering素材）
3. 读取源目录和目标目录的 `.kb-policy.yaml`

## 执行步骤

### 步骤 1：读取源文件

读取待脱敏的 Markdown 文件全文。

### 步骤 2：执行脱敏

使用共享脱敏引擎 `scripts/desensitize_engine.py` 处理文本：

```bash
python3 scripts/desensitize_engine.py <input.md> -o <output.md> --report <report.json>
```

或手动按 `references/identifier-rules.md` 中的规则逐项替换。

### 步骤 3：Markdown 特有处理

| 元素 | 处理方式 |
|------|---------|
| 代码块中的 IP/主机名 | 同样替换（代码块不豁免） |
| 图片 alt 文本 | 检查是否含客户标识 |
| 链接 URL | 检查是否含客户域名 |
| 表格中的数据 | 保留数值，替换标识符 |
| YAML frontmatter | 检查 title/author 字段 |
| 文件路径引用 | 替换含客户名的路径 |

### 步骤 4：验证

- 确认无真实客户名残留
- 确认无真实 IP 残留
- 确认无凭据残留
- 确认 SLA 数值完整保留
- 确认指标结构完整保留

### 步骤 5：重命名输出文件

按命名规范：`主题-客户代号-脱敏.md`

### 步骤 6：生成脱敏报告

报告包含：替换统计、警告（凭据发现）、保留信息确认。

## Markdown 特有注意事项

1. **代码块不豁免**：Markdown 中的代码块（```）内的 IP、主机名同样需要脱敏
2. **图片引用**：`![alt](path)` 中的 path 如果含客户名需要替换
3. **链接**：`[text](url)` 中的 url 如果含客户域名需要替换
4. **表格**：表格中的 SLA 数值保留，但客户名列替换为代号
5. **YAML frontmatter**：检查 title、author、tags 字段是否含客户标识

## 金标准参考

`02-Offering素材/02-SLA与服务治理/SLA-SLO矩阵-MFG-A-脱敏.md`
