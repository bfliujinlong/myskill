---
name: pcs-hld
---

# 高级架构设计生成（pcs-hld）

| 字段 | 值 |
|---|---|
| **description** | 单云高级架构设计（HLD）生成 - 触发条件：目标云已确定（非多云对比阶段），需要产出账号组织/网络/安全合规/IAM/计算/存储/数据库/监控运维 8 大领域的高阶设计时触发；完成判据：8 领域均有设计要点/关键组件/选型理由。目标云尚未选定、仍在多云对比阶段的用 `pcs-arch-selection`；需要具体参数表/部署步骤的下一步用 `mig-lld`（以本 skill 输出为输入）。 |
| **风险等级** | 低风险写 |
| **输入参数** | `facts`（Fact Sheet 结构化对象，必填） |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-31.001 |

对应 AICC 后端内置能力 `Generate-HLD`。

## 触发条件 / 完成判据

触发：`facts` 已就位且目标云已明确（`facts.target_cloud` 非空）。完成：8 大领域
（账号与组织架构/网络架构/安全与合规/IAM/计算/存储/数据库/监控运维）均有设计要点、关键组件、选型理由。

## 判断逻辑（正文）

1. 输入检查：`facts` 缺失或 `target_cloud` 未定 → 交互模式反问；无头模式若目标云未定，
   路由建议改走 `pcs-arch-selection`（多云对比阶段），本 skill **终止并升级**说明原因。
2. 调用 `aicc.execute_skill("Generate-HLD", {"facts": facts})`。
3. `llm_used=false` → confidence 低，提示人工核对安全合规领域的选型理由是否符合客户实际合规要求
   （等保/SOC2/ISO27001 等不能直接套模板）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, domains, design_principles}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`facts` 缺失或目标云未定且无法反问；工具不可达。
打包：已排除（是否已确认目标云）、剩余假设（哪些领域设计是通用模板未按客户定制）、
建议先看安全与合规领域。

## 第〇步：选厂家色系（出稿前必须先定）

目标云 / 甲方生态决定皮肤；无厂家归属时回退安畅红（中立 MSP）。

| 场景 | `--brand` | 主色 | 变体模板 |
|---|---|---|---|
| 目标云 阿里云 / 甲方阿里生态 | `alibaba` | `FF6A00` | `templates/HLD_阿里橙.md` |
| 目标云 腾讯云 / 甲方腾讯生态 | `tencent` | `3370FF` | `templates/HLD_腾讯蓝.md` |
| 中立 / 无明确厂家（默认） | `anchnet` | `C00000` | `templates/HLD_安畅红.md` |
| 目标云 AWS / 甲方 AWS 生态 | `aws` | `232F3E` | `templates/HLD_AWS黑.md` |
| 目标云 Azure / 甲方微软生态 | `azure` | `00477F` | `templates/HLD_Azure浅蓝.md` |

**交付前必过闸门**：`mig-std/doc-audit-gate`（去 AI 味 40 / 事实红线 40 / 版式色系 20）。
红线（虚构人员·证书·案例、金额臆造、占位符残留、数字跨章冲突、RACI 缺位）任一命中即 BLOCK，催也不放。

**色系与厂家口径单一事实源**：`mig-std/brand-doc-kit`
- 取变体模板：`python3 brand-doc-kit/scripts/build_variant.py --type hld --brand <厂家> -o out.md`
- 渲染 docx：`python3 brand-doc-kit/scripts/build_docx.py out.md --brand <厂家> -o out.docx`
- 开箱核验：`python3 brand-doc-kit/scripts/verify_brand_variants.py`（色值 / 附录E / 串用 / 差异度）
