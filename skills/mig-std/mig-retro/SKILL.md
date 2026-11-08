---
name: mig-retro
description: "云迁移项目阶段 06 复盘：汇总做得好/做得差/改进项，产出复盘报告与知识库回写清单（经验教训 + 可复用资产归档项）。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [复盘, 阶段06, 经验教训, 知识沉淀, retro, lessons-learned]
    related_skills: [mig-acceptance, cloud-migration-pm, migration-team, pcs-risk-register]
---

# 项目复盘（阶段 06，mig-retro）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 项目**已完成客户签字验收**、需要组织复盘会并沉淀经验教训与可复用资产（方案模板/IaC 模块/工具脚本）时触发；完成判据：复盘报告含做得好/做得差（含根因）/改进项（含行动计划、责任人、日期）三章 + 知识库回写清单（每条含目标文件与作用）。与 `mig-acceptance` 互斥：**尚未完成验收签字用 `mig-acceptance`**，复盘必须在验收之后；与 `pcs-risk-register` 互斥：风险仍在跟踪中（未闭环）用后者。 |
| **风险等级** | 低风险写（仅产出文档与回写清单；**不自动改任何 skill/知识库文件**，回写需人工确认后执行） |
| **输入参数** | 必填：`project`/`phase`（复盘范围，如「全周期」或「阶段 04 实施」）；选填：`lessons`（结构化经验条目，含 `category`/`what`/`root_cause`/`action`）、`metrics`（工期/成本/缺陷数等实测值）、`retro_date`、`out_dir` |
| **依赖工具** | terminal / read_file / write_file（`scripts/retro_build.py`，stdlib only） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：阶段 05 验收报告已签字；或用户明确要求复盘/项目总结/经验沉淀。
- 完成：① 复盘报告（三章结构 + 检查清单回执）② 知识库回写清单（可执行的归档项）③ 双形态输出（JSON + Markdown）。**改进项必须带责任人与日期，缺一即标「待确认」并计入升级信息。**

## 判断逻辑（正文）

1. **输入检查**：`project`/`phase` 缺失 → 交互模式反问；无头模式终止并升级。
2. **前置校验**：若调用方未声明验收已完成，先提示「复盘应在验收签字后」，仍继续生成但在 `remaining_hypotheses` 记录该前置未确认。
3. **三章展开**：`lessons` 按 `category` ∈ {`做得好`,`做得差`,`改进项`} 归类；`做得差` 条目**必须填 `root_cause`**，缺失则写「根因待分析」并计入升级（不允许含糊带过）；`改进项` 必须填 `owner`+`due_date`，缺失即「待确认」。
4. **指标**：给了 `metrics` 才渲染指标表；**不编造任何数值**，未提供的指标不出现。
5. **知识库回写**：按 category 推导归档动作（做得好 → 沉淀为模板/checklist；做得差 → 补红线或前置检查；改进项 → 待办清单），输出**建议目标路径**，明确写「需人工确认后再写入」。
6. **红线**：不虚构人员、案例、证书；不写价格/单价/人天/月费；未核实写「待确认」。

## 输出双形态

- 结构化 JSON：`{conclusion, confidence, suggested_action, escalation_reason, sections, metrics, kb_writebacks, checklist}`
- 人类可读：`out_dir/项目复盘报告.md`、`out_dir/知识库回写清单.md`（黑灰配色、无蓝、去 AI 味）

## 升级契约

触发：必填输入缺失且无法反问；`做得差` 条目缺根因；`改进项` 缺责任人/日期；验收未确认完成就要求复盘；用户要求自动写入知识库（超出边界）。
打包：`ruled_out`（已排除：验收是否已签字、metrics 是否经 PM 确认）、`remaining_hypotheses`（哪些根因待分析、哪些改进项缺 owner）、`first_checks`（先看缺 owner/due_date 的改进项，再看根因待分析的条目）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-retro/scripts/retro_build.py \
   --input input.json --out-dir ./out
```

`input.json` 结构见 `templates/input.example.json`；先跑 `--self-test` 验证脚本可用。
