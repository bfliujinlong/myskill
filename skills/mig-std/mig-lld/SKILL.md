---
name: mig-lld
---

# 详细架构设计生成（mig-lld）

| 字段 | 值 |
|---|---|
| **description** | 详细架构设计（LLD）生成 - 触发条件：已有 HLD 摘要，需要落地到网络拓扑/计算实例规格/数据库规格/
安全合规清单/监控告警配置/部署步骤的具体参数时触发；完成判据：六类具体参数/步骤均产出。
本 skill 的前置是 `mig-hld`（HLD 未产出时不触发）。 |
| **风险等级** | 低风险写 |
| **输入参数** | 必填：`hld_summary`/`target_cloud`；选填：`region` |
| **依赖工具** | aicc.execute_skill |
| **版本** | 2026-10-31.001 |

对应 AICC 后端内置能力 `Generate-LLD`。

## 触发条件 / 完成判据

触发：`hld_summary`/`target_cloud` 已知。完成：网络拓扑（CIDR/路由表/安全组）、计算实例规格表、
数据库规格表、安全合规清单、监控告警配置项、部署步骤（Terraform/ROS）均产出。

## 判断逻辑（正文）

1. 输入检查：`hld_summary` 缺失 → 无头模式查上游 `mig-hld` 输出是否存在，取其 `domains` 摘要作为
   `hld_summary`；仍缺失则**终止并升级**（LLD 没有 HLD 做不出有意义的具体参数）。
2. 调用 `aicc.execute_skill("Generate-LLD", {hld_summary, target_cloud, region})`。
3. `llm_used=false` → confidence 低，提示人工核对部署步骤（Terraform/ROS 模板）里的资源规格是否
   匹配 `target_cloud` 实际可用的实例/数据库型号（mock 容易产出不存在的规格名）。

## 输出双形态

结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, network_topology, compute_specs, database_specs, security_checklist, monitoring_config, deployment_steps}`。
人类可读：AICC 后端生成的 DOCX。

## 升级契约

触发：`hld_summary`/`target_cloud` 缺失且无法反问；工具不可达。
打包：已排除（是否已跑过 mig-hld）、剩余假设（region 缺失时按目标云默认 region 填充）、
建议先看 compute_specs/database_specs 的型号是否真实存在。

## 第〇步：选厂家色系（出稿前必须先定）

目标云 / 甲方生态决定皮肤；无厂家归属时回退安畅红（中立 MSP）。

| 场景 | `--brand` | 主色 | 变体模板 |
|---|---|---|---|
| 目标云 阿里云 / 甲方阿里生态 | `alibaba` | `FF6A00` | `templates/LLD_阿里橙.md` |
| 目标云 腾讯云 / 甲方腾讯生态 | `tencent` | `3370FF` | `templates/LLD_腾讯蓝.md` |
| 中立 / 无明确厂家（默认） | `anchnet` | `C00000` | `templates/LLD_安畅红.md` |
| 目标云 AWS / 甲方 AWS 生态 | `aws` | `232F3E` | `templates/LLD_AWS黑.md` |
| 目标云 Azure / 甲方微软生态 | `azure` | `00477F` | `templates/LLD_Azure浅蓝.md` |

**交付前必过闸门**：`mig-std/doc-audit-gate`（去 AI 味 40 / 事实红线 40 / 版式色系 20）。
红线（虚构人员·证书·案例、金额臆造、占位符残留、数字跨章冲突、RACI 缺位）任一命中即 BLOCK，催也不放。

**色系与厂家口径单一事实源**：`mig-std/brand-doc-kit`
- 取变体模板：`python3 brand-doc-kit/scripts/build_variant.py --type lld --brand <厂家> -o out.md`
- 渲染 docx：`python3 brand-doc-kit/scripts/build_docx.py out.md --brand <厂家> -o out.docx`
- 开箱核验：`python3 brand-doc-kit/scripts/verify_brand_variants.py`（色值 / 附录E / 串用 / 差异度）
