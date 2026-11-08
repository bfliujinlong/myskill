---
name: mig-operation-manual
description: "云迁移阶段 03 运维手册：按网络/安全/计算/存储/数据库/监控/割接七域生成标准化 Runbook 集（五要素：触发/前置/步骤/验证/回滚），输出 operation_manual.md + json。触发词：运维手册、Runbook、操作手册、runbook、运维 SOP、巡检手册。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段03, 运维手册, Runbook, 五要素, 回滚, 割接红线, 双语]
    related_skills: [mig-lld, mig-cutover-plan, mig-acceptance, mig-sizing-advice, mig-datasync, mig-retro]
---

# 云迁移运维手册 / Operation Manual（阶段 03，mig-operation-manual）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 迁移实施与接管阶段，需要**可直接交给运维执行**的操作手册（Runbook 集）时触发。完成判据：每条 Runbook 五要素（trigger / precheck / steps / verify / rollback）齐全，缺任一项标 `incomplete` 并进待补清单、**不伪造步骤**；缺 `rollback` 额外打 `no_rollback` 红线并单列「不得进入正式割接清单」；云特有命令仅在有事实源（`CLOUD_CMD`，当前 alicloud / aws）时输出，否则一律「待确认（须查目标云官方文档）」，**绝不臆造 CLI**；输出 md + json 双形态，且**全文无金额/单价/人天**。**与 `mig-lld` 区别**：LLD 给设计参数（网段/规格/安全组矩阵），本 skill 给「怎么操作、怎么回滚」的步骤；**与 `mig-cutover-plan` 区别**：后者定割接范围/批次/窗口/组织，本 skill 给割接的具体操作步骤与回滚动作；**与 `mig-acceptance` 区别**：验收产出用例与判据，本 skill 产出操作指引；**与 `pcs-quotation` 互斥**：本 skill 绝不产金额。 |
| **风险等级** | 低风险写（仅产出文档；**不执行任何生产变更、不停资源、不改客户环境**；手册内命令须在变更窗口内经审批后由人工执行） |
| **输入参数** | 必填：`project`、`target_cloud`。选填：`source_cloud`、`owner`（缺省→待确认）、`domains`（缺省=全部 7 域；未知域报 `ValueError` 不静默）、`runbooks[]`（项目特有补充，字段：`id`/`title`/`domain`/`env`/`owner`/`trigger`/`precheck`/`steps`/`verify`/`rollback`） |
| **依赖工具** | terminal（`scripts/operation_manual.py`，stdlib only，无第三方依赖） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：方案已定（LLD/选型完成）或实施期已启动，客户/运维团队要求「迁移后怎么运维」「割接怎么操作」「出问题怎么回滚」；或投标/方案包要求附运维手册。
- 完成：① 覆盖请求域（默认 7 域 × 2 条 = 14 条骨架）② 每条五要素齐全或明确标「待补」③ 无回滚的项全部进红线清单 ④ 每条有责任人（未指定→「待确认」不代填人名）⑤ 命令只来自事实源 ⑥ md + json 双形态 ⑦ **全文零金额/单价/人天**。

## 判断逻辑（正文）

1. **七域骨架**：`network` / `security` / `compute` / `storage` / `database` / `monitoring` / `cutover`，每域 2 条默认 Runbook（VPC 与安全组开通、专线 VPN、IAM 最小权限、密钥轮换、ECS 创建与升降配、对象存储迁移与生命周期、数据库迁移与恢复演练、监控告警与日志留存、割接演练与正式割接）。
2. **五要素强校验**：`trigger`/`precheck`/`steps`/`verify`/`rollback` 任一为空串、空列表或 `None` → 该条 `incomplete` 并进 `todo`。**核心红线：不为凑齐全而编造步骤**，缺就是缺，交由现场补。
3. **割接红线（no_rollback）**：缺 `rollback` 的 Runbook 视为**不可执行**，除 `incomplete` 外额外打 `no_rollback`，在 md 中单列「🚩 无回滚方案」章节，写明不得进入正式割接清单。
4. **命令事实源 `CLOUD_CMD`**：当前仅 `alicloud`（`aliyun ecs RunInstances`、`ossutil cp`/`ls`）与 `aws`（`aws ec2 run-instances`、`aws s3 sync`/`ls`）的计算/存储/监控域。其他云、其他域一律输出 `NO_FACT_NOTE`（待确认，须查官方文档），**绝不编 CLI 参数**。
5. **责任人不代填**：无 `owner` → 「待确认（未指定责任人，交付前必须落实到人）」，禁止虚构姓名。
6. **域校验不静默**：传入未知 `domain` 直接 `ValueError` 并列出可选域，避免拼写错误被吞掉导致手册漏域。
7. **红线**：① **不输出任何金额/单价/人天**（运维与报价分离，金额一律由 `pcs-quotation` 出具）；② 不执行生产变更，只产文档；③ 不虚构客户资源、系统名、人员。

## 输出双形态

- `operation_manual.md`：头部（源→目标云 / 责任人 / 覆盖域 / 统计 / 口径声明）+ 按域汇总表（Runbook 数 / 齐全 / 待补 / 无回滚）+ 逐条明细（环境、责任人、触发、前置检查、步骤、参考命令、验证、回滚、待补项）+ 🚩 无回滚清单 + 待确认清单。
- `operation_manual.json`：结构化，含 `items[]`、`todo`、`no_rollback`、`stats{total, complete, incomplete, no_rollback}`，供 `mig-cutover-plan` / `mig-acceptance` / `mig-retro` 消费。

## 升级契约

触发：`no_rollback` 清单非空且已进入割接准备期（回滚缺失属重大风险）；`incomplete` 占比 >20%（说明现场运维信息不足）；客户要求手册内直接给具体命令但该云无事实源（须先查官方文档补 `CLOUD_CMD`，不得让模型凭记忆写命令）。
打包：`ruled_out`（目标云/责任人是否已确认、命令事实源是否已核）、`remaining_hypotheses`（缺五要素的条目、无事实源的域）、`first_checks`（先补回滚方案→再补缺失要素→再核命令事实源→最后才进割接演练）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-operation-manual/scripts/operation_manual.py --self-test
$PY ~/.hermes/skills/mig-std/mig-operation-manual/scripts/operation_manual.py \
   --input examples/customer-ops.json --out-dir ./out
```

输入结构见 `scripts/operation_manual.py` 文件头 docstring；`examples/customer-ops.json` 为真实客户样例（7 域全量 + 2 条自定义：RB-DNS-01 五要素齐全，RB-DB-ORA-01 故意留空 rollback 以触发割接红线），跑出 total 16 / complete 15 / incomplete 1 / no_rollback=[RB-DB-ORA-01]。
