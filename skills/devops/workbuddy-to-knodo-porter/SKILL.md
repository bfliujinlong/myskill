---
description: "Use when 把WorkBuddy/CodeBuddy格式插件移植为Knodo/Claude Code格式."
name: workbuddy-to-knodo-porter
version: 1.0.0
author: jinlongliu
license: MIT
platforms: [linux, mac, windows]
metadata:
  hermes:
    tags: [skill, plugin, port, convert, workbuddy, codebuddy]
---

# WorkBuddy → Knodo Porter

## 描述
.codebuddy-plugin/plugin.json+agents/*.md → Knodo SKILL.md + Claude Code .claude/ 格式。

## 转换规则

| WorkBuddy字段 | Knodo字段 |
|---------------|----------|
| name | name (frontmatter) |
| description | description (frontmatter) |
| agents[].id | 子技能名 |
| agents[].system_prompt | body角色定义 |
| skills[].trigger | 触发条件 |
| tools | 工具列表 |

## 脚本

```bash
python3 workbuddy-to-knodo.py convert .codebuddy-plugin/
python3 workbuddy-to-knodo.py convert .codebuddy-plugin/ -o ~/.hermes/skills/
```

## 限制
- 仅转文本，不验证代码
- 工具名需人工核对