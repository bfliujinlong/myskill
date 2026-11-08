---
name: mig-delivery-orch
description: "云迁移阶段 04 实施编排：按业务迁移/LandingZone/大数据迁移/Well-Architected 四条轨道展开 151 条真实 Action 看板，计算阶段工时、阶段出口门禁、依赖关系、关键路径与工作日日历，输出 delivery_orch.md + json。触发词：实施编排、交付编排、实施计划、交付计划、Action 看板、任务编排、实施排期、工时看板。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段04, 实施编排, 交付编排, Action库, 门禁, 排期, 双语]
    related_skills: [mig-cutover-plan, mig-cutover-wave, mig-datasync, mig-operation-manual, pcs-wbs-migration, pm, pcs-quotation]
---

# 云迁移实施编排 / Delivery Orchestration（阶段 04，mig-delivery-orch）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 进入实施阶段，需要把「要做什么事、按什么顺序做、每阶段出口卡什么、谁阻塞了」落成一张**可执行编排表**时触发。完成判据：Action 库**全部来自客户执行计划看板真表**（4 轨道共 151 条），未知 `track`/未知 action id **直接报错**而非静默吞掉；每个阶段末自动插一条**出口门禁**，无事实判据的阶段标「待确认，不得臆造」；`done`/`blocked` 回填后出完成率；有 `start_date` 才出日历日且**跳过周末**。**与 `mig-cutover-plan`/`mig-cutover-wave` 区别**：后两者只编排**割接窗口内的批次与切换动作**，本 skill 编排**从售前到交付收尾的全周期 Action**；**与 `pcs-wbs-migration` 区别**：WBS 给通用工作分解结构与金额，本 skill 给**真实看板工时与依赖**，且**零金额**；**与 `mig-operation-manual` 区别**：手册给「怎么操作、怎么回滚」的步骤，本 skill 给「什么时候做、谁卡住、工期多长」的编排与排期；**与 `pcs-quotation` 互斥**：本 skill 绝不产金额，只出工时（h）与工作日。 |
| **风险等级** | 低风险写（仅产出文档；**不执行任何生产变更、不停资源、不改客户环境**） |
| **输入参数** | 必填：`project`、`track`（`business-migration`\|`landing-zone`\|`bigdata-migration`\|`well-architected`）。选填：`start_date`（YYYY-MM-DD）、`hours_per_day`（默认 8）、`team_size`（默认 2）、`scale`（0<scale≤20，默认 1.0）、`done[]`、`blocked[{id,reason}]`、`extra_actions[{id,name,phase,trigger,hours,priority,depends_on}]`、`depends_on{id:[前置]}` |
| **依赖工具** | terminal（`scripts/delivery_orch.py`，stdlib only，无第三方依赖） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：项目进入实施期，PM/交付负责人要「任务编排表」「工时看板」「阶段门禁」「谁阻塞了」「什么时候能做完」；或周报/客户汇报需要带依赖与关键路径的实施计划。
- 完成：① track 的 Action 数与阶段数与看板真表一致（46/9、41/8、34/9、30/7）② 每阶段有出口门禁且无判据者标待确认 ③ done/blocked 正确回填 ④ 依赖默认同阶段串接、支持显式覆盖 ⑤ 关键路径非空 ⑥ 有 `start_date` 时起止日**全部落在工作日** ⑦ **全文零金额/单价/人天**。

## 判断逻辑（正文）

1. **Action 库只来自真表**：`TRACKS` 内置 4 轨道共 151 条 Action，字段为阶段 / 触发（👋人工·🤖自动·📄文档）/ 工时 h / 优先级。**绝不臆造任务**；未知 `track`、未知 action id、未知 `blocked` id 一律 `OrchError`（退出码 2），不静默忽略。
2. **阶段出口门禁**：每个阶段末插一条 gate，判据取自 `GATE_CRITERIA`（如「实施部署」= 生产资源就绪 + 全量增量同步完成 + 业务联调通过）。阶段不在表内 → `DEFAULT_GATE`「待确认，须现场补，不得臆造」，并在 md 待确认章节列出。
3. **依赖**：默认「同阶段内按序串接 + 跨阶段接上一阶段末项」；用户可用 `depends_on` 显式覆盖。**默认串接下关键路径必然覆盖全部 Action**，此时 md 显式声明「最保守的串行下界」，避免被误读为真实瓶颈。
4. **排期**：ES/EF 工时累加；关键路径沿 EF 最大者回溯 `depends_on`；**仅当提供 `start_date` 才出日历日**，且用 `add_workdays` **跳过周六周日**。无 `start_date` → 只出工时，**不编造日期**。
5. **`scale` 工时缩放**：应用数/数据量超基线时上调（0<scale≤20），越界报错。
6. **`done`/`blocked` 回填**：`done` 计入完成工时与完成率；`blocked` 无 `reason` 时落默认文案「（原因未填，交付前须说明）」，不代编理由；`done` 中含非本 track 的 id 列入待确认。
7. **`extra_actions` 校验**：`id` 必填且不得与内置重复、`phase` 必须存在、`hours` 必须为数字，任一不符报错。
8. **红线**：① **不输出任何金额/单价/人天/月费**，只出工时（h）与工作日，报价一律由 `pcs-quotation` 出具；② 不臆造任务、不虚构进度、不虚构人员；③ 不执行生产变更。

## 输出双形态

- `delivery_orch.md`：头部（轨道 / Action 数 / 阶段数 / 工时与完成率 / 状态分布 / 日历与排期假设）+ 一、阶段汇总与出口门禁表 + 二、关键路径 + 三、Action 明细（按阶段，含 ID·任务·触发·工时·优先级·依赖·状态·起止日·关键路径标记）+ 四、🚩 阻塞清单 + 五、待确认项 + 六、口径声明（零金额）。
- `delivery_orch.json`：结构化，含 `phases[]`（含 `gate.criteria`/`gate.known`）、`actions[]`（含 `depends_on`/`status`/`critical`）、`critical_path`、`stats{total_actions,done,blocked,pending,total_hours,done_hours,open_hours,pct}`、`calendar`，供 `pm` / `mig-cutover-plan` / `mig-acceptance` / `mig-retro` 消费。

## 升级契约

- 客户看板新增 Action / 阶段 → 扩 `TRACKS` 并同步自检断言的条数与阶段数。
- 新增阶段 → 同时在 `GATE_CRITERIA` 补事实判据；**无判据则保持 `known=False`，不得编造**。
- 需要金额 → 走 `pcs-quotation`；需要合同/SLA → 走 `pcs-sow-generator`；需要通用 WBS → 走 `pcs-wbs-migration`。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
SK=~/.hermes/skills/mig-std/mig-delivery-orch

# 自检（11/11）
$PY $SK/scripts/delivery_orch.py --self-test

# 出编排表
$PY $SK/scripts/delivery_orch.py --input $SK/examples/customer-orch.json --out-dir ./out
```

## 示例

`examples/customer-orch.json` → 项目 `C-Customer CHINA M2C`，轨道 `business-migration`，`start_date 2026-11-03`，8h/人日 × 2 人并行，已完成 5 项、阻塞 1 项（专线未开通）、补充 1 项。

实跑结果：**47 项 / 9 阶段 / 120 h / 完成率 8.3% / 剩余 110 h**；日历 2026-11-03 → 2026-11-12（8 个工作日，已跳过周末）；阻塞 `A-035`。
