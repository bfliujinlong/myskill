---
name: solution-delivery
description: "方案交付工程师：一键产出三类交付物——①架构图（输出标准 .drawio 文件，draw.io/Visio 均可打开，可选 .vdx）；②快速 Demo（生成可演示的 HTML 原型/CLI 脚本）；③方案文档（结构化 markdown，可转 Word/PDF）。触发词：画架构图、输出 drawio、输出 visio、做 demo、快速演示、出方案、技术方案、方案文档、架构设计。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [架构图, drawio, visio, demo, 方案, 交付, 原型]
    related_skills: [presales-architect, business-development, roles-database, roles-bigdata]
---

# 方案交付工程师（Solution Delivery）

把"画架构图 / 做 demo / 出方案"三件事标准化产出**文件**，而不是只在对话里说。

## When to Use
- 用户要"画个架构图" → 产出 `.drawio` 文件（draw.io 原生，Visio 可导入）
- 用户要"做个 demo / 快速演示" → 产出可打开的 HTML 原型 或 Python/Shell 脚本
- 用户要"出方案 / 技术方案" → 产出结构化 markdown 文档

## 核心能力

### 1. 架构图 → .drawio
用 `templates/drawio-gen.py` 生成标准 draw.io XML。调用方式：
```
python3 ~/.hermes/skills/solution-delivery/templates/drawio-gen.py <输出文件.drawio> \
  --title "系统架构" \
  --nodes "用户层:web:客户/渠道" "接入层:lb:SLB/API网关" "应用层:app:微服务" "数据层:db:MySQL/PolarDB" \
  --edges "用户层->接入层" "接入层->应用层" "应用层->数据层"
```
节点格式：`名称:形状:说明`；形状支持 `web|lb|app|db|cloud|storage|queue|fw|default`。
输出是合法 draw.io 文件，浏览器打开 draw.io 或桌面版即可编辑，Visio 可"导入→XML"。

### 2. 快速 Demo → HTML 原型
用 `templates/demo-html.py` 生成单文件 HTML 演示页（深色科技风，离线可用）：
```
python3 ~/.hermes/skills/solution-delivery/templates/demo-html.py <输出.html> \
  --title "客户门户 Demo" --sections "登录:账号密码登录" "控制台:资源概览卡片" "监控:实时图表"
```
适合售前给客户看交互效果，纯前端无需后端。

### 3. 方案文档 → markdown
用 `templates/solution-doc.md` 作为骨架，填充：背景/需求、总体架构、技术选型、资源清单、迁移步骤、风险与对策、报价摘要、实施计划。

## 输出位置
默认保存到用户指定路径；未指定则放当前工作目录，文件名带项目名前缀。

## 注意
- 架构图用 draw.io 原生 mxGraph XML（不是 PNG/SVG），保证可二次编辑。
- Demo HTML 不依赖外部 CDN（离线可用），如需图表用内联 SVG/Canvas。
- 方案文档用中文，表格化呈现资源与报价。
