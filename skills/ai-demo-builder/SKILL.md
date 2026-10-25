---
name: ai-demo-builder
description: "AI 演示方案工厂：一句话启动客户演示方案生产流水线。四个 Workflow——① AI 落地痛点发现 → ② 客户画像建模 + Demo 矩阵设计 → ③ 方案网页 + Demo 三件套生产 → ④ 跑通验证 + 交付。触发词：演示方案、客户演示、demo 设计、销售赋能演示、合作伙伴演示、培训方案、场景案例制作、AI 场景案例。"
version: 1.0.0
author: Hermes Agent (ported from WorkBuddy SkillHub ai-demo-builder)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [演示, demo, 售前, 方案, 客户, 销售赋能, 场景案例]
    related_skills: [solution-delivery, presales-architect, business-development, sales]
---

# AI 演示方案工厂（AI Demo Builder）

把"做一份客户演示方案"从手工活变成标准化流水线。给客户名/行业/角色任一输入，自动跑完四个 Workflow。

## Workflow 1 — AI 落地痛点发现
- 问清：客户行业、规模、当前痛点、决策链。
- 产出：痛点清单（按影响/紧迫度排序）。
- 参考：`references/pain-points.md`

## Workflow 2 — 画像建模 + Demo 矩阵
- 建客户画像（角色、KPI、顾虑）。
- 设计 Demo 矩阵：每个痛点对应一个可演示场景。
- 参考：`references/scenario-library.md`（已验证场景库）

## Workflow 3 — 生产（方案网页 + Demo 三件套）
- 方案网页：调用 `solution-delivery` skill 的 `demo-html.py` 生成深色科技风演示页。
- Demo 三件套：
  1. 架构图（`.drawio`，用 `solution-delivery` 的 `drawio-gen.py`）
  2. 演示脚本（会话级 step-by-step）
  3. 价值卡片（一句话价值主张）
- 资料包：README 索引 + 验证报告模板。
- 模板见 `templates/`。

## Workflow 4 — 验证 + 交付
- 自检清单（见 `workflows/04-validation.md`）：网页可打开？架构图合法？演示脚本可复现？
- 交付：把产物打包到指定目录，输出 README 索引。

## 行业素材
`references/industries.md` 含 9 大行业（制造/金融/医疗/零售/政府/教育/能源/物流/互联网）的痛点与 Demo 锚点。

## 输出物清单
- `方案网页.html`（4 风格可选，默认深色）
- `架构图.drawio`
- `演示脚本.md`
- `价值卡片.md`
- `README.md` 索引
- `验证报告.md`

## 注意
- 所有产物纯本地生成，零外部 API 依赖，免费机可跑。
- 演示数据用脱敏/虚构样本，不夹带真实客户敏感信息。
