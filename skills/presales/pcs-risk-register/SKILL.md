---
name: pcs-risk-register
---

# 项目风险登记册生成（pcs-risk-register）

| 字段 | 值 |
|---|---|
| **description** | 项目全生命周期风险登记册生成 - 触发条件：项目类型/规模已知，需要产出至少 10 条覆盖技术/人员/进度/成本/合规/外部六类的风险登记册时触发；完成判据：至少 10 条风险，每条含概率/影响/等级/缓解措施/应急方案/责任人/触发条件。与 `pcs-risk-assessment`（专注安全风险、输入是架构描述）互斥：项目管理类综合风险用本 skill，纯安全风险用 `pcs-risk-assessment`。 |
| **风险等级** | 只读（风险识别与登记，不产生任何系统变更） |
| **输入参数** | 必填：`project_type`；选填：`project_scale`/`team_size`/`timeline_months` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Risk-Register`。

## 触发条件 / 完成判据

触发：`project_type` 已知。完成：至少 10 条风险，每条含风险编号/描述/类别/概率/影响/等级（颜色）/
缓解措施/应急方案/责任人/触发条件。

## 判断逻辑（正文）

1. 输入检查：`project_type` 缺失 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("Risk-Register", {project_type, project_scale, team_size, timeline_months})`。
3. `llm_used=false` → confidence 低，提示人工核对风险条目是否贴合实际项目（mock 容易产出通用化、
   未结合实际团队规模/周期的风险描述）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, risks, summary_by_category}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`project_type` 缺失且无法反问；工具不可达。
打包：已排除（无）、剩余假设（team_size/timeline_months 缺失时风险等级估算偏保守）、
建议先看等级为"高"的风险条目是否有责任人。
