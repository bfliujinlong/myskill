---
name: pcs-lz-estimate
---

# Landing Zone 成本估算（pcs-lz-estimate）

| 字段 | 值 |
|---|---|
| **description** | Landing Zone 项目人天与成本估算 - 触发条件：账号数/Region 数/目标云已知，需要产出 LZ 实施工作量明细+人天汇总+成本明细时触发；完成判据：工作量明细（账号开通/网络规划/安全基线/IAM/监控）+按角色人天汇总+成本明细+风险点均产出。专用于 Landing Zone 项目，不用于通用迁移报价（见 `pcs-quotation`）。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`account_count`/`region_count`/`target_cloud`；选填：`vpc_count`/`security_level`/`multi_account` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-29.001 |

对应 AICC 后端内置能力 `Estimate-LZ`。

## 触发条件 / 完成判据

触发：`account_count`/`region_count`/`target_cloud` 已知。完成：工作量明细（账号开通/网络规划/
安全基线/IAM/监控等）、按角色人天汇总、成本明细（人天成本+云资源成本）、风险点均产出。

## 判断逻辑（正文）

1. 输入检查：三个必填字段缺失一项 → 交互模式反问；无头模式终止并升级。
2. 调用 `aicc.execute_skill("Estimate-LZ", {account_count, region_count, vpc_count, security_level, target_cloud, multi_account})`。
3. `llm_used=false` → confidence 低，提示人工核对人天单价与 `pcs-quotation` 的 `references/ac-mig-pricing.md`
   口径是否一致（避免同一客户两份报价口径不统一）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, person_days_by_role, cost_breakdown, total_person_days, total_cost, risks}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：必填字段缺失且无法反问；工具不可达。
打包：已排除（无）、剩余假设（multi_account 未明确时按单账号估算）、建议先看 cost_breakdown 里
云资源成本部分是否按目标云真实刊例。
