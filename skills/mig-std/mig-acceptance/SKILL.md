---
name: mig-acceptance
description: "云迁移项目阶段 05 验收：从 SOW 交付物清单 + 系统清单生成 UAT 用例清单与验收报告（含遗留问题与签字项）。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [验收, UAT, 阶段05, 交付物, 签字, acceptance]
    related_skills: [mig-cutover-wave, mig-lld, pcs-sow, cloud-migration-pm, migration-team]
---

# 项目验收（阶段 05，mig-acceptance）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 项目进入验收阶段，需要**对照 SOW 交付物清单**生成 UAT 用例清单、汇总测试结果、输出验收报告（含遗留问题处理计划与客户签字项）时触发；完成判据：UAT 用例覆盖 8 个技术域 + 业务功能且与 SOW 交付物逐条可追溯，验收报告含通过率/遗留问题/签字栏。与 `mig-cutover-wave` 互斥：还在排波次切换计划用 `mig-cutover-wave`；与 `mig-retro` 互斥：客户已签字、要做经验沉淀用 `mig-retro`。 |
| **风险等级** | 低风险写（仅产出文档；**不执行任何生产变更、不停资源、不改客户环境**） |
| **输入参数** | 必填：`project`（客户/项目名）/`target_cloud`/`deliverables`（SOW 交付物清单，每项含 `id`+`name`）/ `systems`（验收系统清单，每项含 `name`+`domains`）；选填：`results`（用例执行结果 `case_id`+`status`+`note`）、`out_dir` |
| **依赖工具** | terminal / read_file / write_file（`scripts/acceptance_build.py`，stdlib only） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：项目已完成实施/割接，进入阶段 05；已有 SOW 交付物清单与被验收系统清单。
- 完成：产出 ① UAT 用例清单（每域 ≥1 条，带 `case_id`/前置条件/步骤/预期结果/对应 SOW 交付物 id）② 验收报告（交付物逐项对照 + 用例通过率 + 遗留问题及处理计划 + 签字栏）③ 双形态输出（JSON + Markdown）。

## 判断逻辑（正文）

1. **输入检查**：`project`/`target_cloud`/`deliverables`/`systems` 任一缺失 → 交互模式反问；无头模式终止并升级（不猜测交付物，避免废标级虚构）。
2. **用例生成**：按域模板展开（网络→安全→IAM→计算→存储→数据库→大数据→监控运维，域顺序取自 `learning/_shared/cloud_profiles/README.md`）+ 每个系统 1 条业务功能用例。域用例只从 `systems[].domains` 实际声明的域展开，**未声明的域不生成**（不编造）。
3. **交付物追溯**：每条用例带 `deliverable_ref`，指向 `deliverables[].id`；无对应交付物时填 `"待确认"` 而非伪造 id。
4. **结果汇总**（给了 `results` 才做）：统计 pass/fail/blocked/未执行；**有 fail 或 blocked 即验收结论=不通过**，必须写入遗留问题与处理计划。
5. **红线**：报告里不出现价格/单价/人天/月费；不虚构人员与案例；未核实项写「待确认」。
6. **目标云差异**：读 `learning/_shared/cloud_profiles/{target_cloud}.md` 取该云 8 域产品锚点做用例落点；profile 缺失时用例落点写「待确认」并在 `remaining_hypotheses` 中记录。

## 输出双形态

- 结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, deliverables_check, uat_cases, summary, open_items}`
- 人类可读：`out_dir/UAT用例清单.md`、`out_dir/验收报告.md`（黑灰配色、无蓝、去 AI 味）

## 升级契约

触发：必填输入缺失且无法反问；`deliverables` 为空（无法建立追溯）；存在 fail/blocked 且客户要求「先签字后整改」；用户要求本 skill 执行生产变更。
打包：`ruled_out`（已排除：交付物清单是否经客户确认、用例是否已过评审）、`remaining_hypotheses`（哪些域缺少 profile 支撑、哪些用例结果未回填）、`first_checks`（先看 fail/blocked 用例的处理计划是否齐，再看遗留问题是否都有责任人与日期）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-acceptance/scripts/acceptance_build.py \
   --input input.json --out-dir ./out
```

`input.json` 结构见 `templates/input.example.json`；先跑 `--self-test` 验证脚本可用。
