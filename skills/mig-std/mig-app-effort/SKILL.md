---
name: mig-app-effort
description: "云迁移应用级工作量估算引擎：四维度评分(D1架构/D2数据/D3耦合/D4改造) → L1-L5 等级 → 基准人天 → 修正系数连乘 → 四阶段拆分 → 团队与角色人天汇总，供报价输入。触发词：应用工作量、人天估算、L1-L5、四维度评分、报价前估算、迁移工时。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段03, 应用评估, 工作量, 人天, L1-L5, 四维度, 报价输入, effort]
    related_skills: [mig-survey-table, pcs-quotation, pcs-wbs-migration, bigdata-migration-assessment, software-coupling-analysis]
---

# 应用级工作量估算（阶段 03，mig-app-effort）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 已有**应用清单**（每个应用带四维度评分）需要折算成**迁移工作量人天**并作为报价输入时触发。完成判据：每个应用完成 D1-D4 评分 → 平均 → L1-L5 定级 → 基准人天 × 修正系数 → 按 4 阶段拆分 → 团队/角色人天汇总，输出三形态（md/xlsx/json），低/中/高三档人天。**与 `presales/pcs-quotation` 互斥**：本 skill 只出**工作量**，对外报价的**最终金额/单价/折扣一律走 `pcs-quotation`**（金额口径唯一）；**与 `bigdata-migration-assessment` 互斥**：大数据域（Hive/HDFS/Spark/数仓）应用走前者；**与 `mig-survey-table` 互补**：第 1 次调研收清单、本 skill 做第 2 次应用级深化估算。 |
| **风险等级** | 低风险写（仅产出文档与计算；不执行任何生产变更、不停资源、不改客户环境） |
| **输入参数** | 必填：`project`/`source_cloud`/`target_cloud`/`apps[]`（每项含 `id`+`name`+`d1`+`d2`+`d3`+`d4`，各维度 1-5 整数）；选填：`apps[].team`（团队分组）、`apps[].factors`（`automation`/`doc_missing`/`bandwidth`/`compliance` 布尔）、`apps[].other_factor`、`price_mode`（`cost`/`list`）、`out_dir` |
| **依赖工具** | terminal（`scripts/app_effort_build.py`，stdlib only；`openpyxl` 可选，缺失时降级为 md/json 并显式说明） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：客户已提供应用清单与四维度评分（或由 `mig-survey-table` 第 1 次调研收集后回填）；需要为报价、WBS、资源阵型提供工作量依据。
- 完成：① 每个应用定级到 L1-L5 并给出基准人天区间 ② 修正系数逐条列出并可追溯 ③ 按「调研设计 .20 / 环境迁移 .30 / 适配调试 .30 / 验收割接 .20」拆分 ④ 团队与角色人天汇总 ⑤ 低/中/高三档总人天 ⑥ 三形态产物齐全。

## 判断逻辑（正文）

1. **输入校验**：必填缺失或维度评分越界（非 1-5）→ 无头模式 `rc=2` 并说明原因，**绝不猜数补默认值**（猜数=废标级风险）。
2. **定级**：`avg = (d1+d2+d3+d4)/4`，按 `LEVELS` 区间映射（L1 1.0-1.8 / 5-7 人天，L2 1.8-2.6 / 7-12，L3 2.6-3.4 / 15-25，L4 3.4-4.2 / 30-50，L5 4.2-5 / 60-90）。
3. **修正系数连乘**：自动化工具 ×0.8、文档缺失 ×1.5、带宽限制 ×1.2、合规额外 ×1.3。自定义 `other_factor` **必须带理由**，否则 `rc=2`（防止拍脑袋改数）。
4. **阶段拆分**：按 `PHASES` 权重把每个应用的低/高人天摊到 4 个阶段（权重合计校验 = 1.0，代码内置断言）。
5. **汇总**：按 `team` 分组汇总团队人天（缺失 `team` 归入「未分组」并告警，不臆造团队名）。
6. **金额（可选且非默认）**：仅当显式传 `price_mode` 时按角色占比（PM .1329 / 架构 .2601 / 云工程师 .5256 / DBA .0814）× 单价折金额，用于**内部成本测算参考**。**默认不输出金额**——对外金额唯一口径在 `pcs-quotation`。
7. **红线**：不虚构应用、不虚构评分事实、不虚构人员与案例；缺评分依据的应用全部记入告警清单并标注「待确认」；评估文档正文**不出现单价与对外报价**。

## 基准参数（改动 = 改报价口径）

常量集中于 `scripts/app_effort_build.py` 顶部 `LEVELS`/`PHASES`/`FACTORS`/`ROLES`，与用户模板 `E93A9503…xlsx`（等级/权重/系数）与 `1CE382BE…xlsx`（单价/产能）对齐。**修改这些数字需商务同意**（沿用 `bigdata-migration-assessment/references/baseline-params.md` 的纪律声明）。

## 输出三形态

- `应用工作量评估.md`（黑灰配色口径、无蓝、去 AI 味；含方法说明、团队汇总、阶段拆分、应用明细、告警清单）
- `应用工作量评估.xlsx`（总览 / 团队汇总 / 应用明细 / 阶段拆分 sheet）
- `app_effort.json`（结构化，供 `pcs-quotation`/`pcs-wbs-*` 下游消费）

## 升级契约

触发：应用清单为空或全部缺 D1-D4 评分；出现自定义系数但无理由；用户要求本 skill 直接输出**对外报价**或合同条款；要求执行生产变更。
打包：`ruled_out`（已排除：评分是否经客户/架构评审、单价是否为当期刊例）、`remaining_hypotheses`（哪些应用缺评分依据、哪些系数缺理由）、`first_checks`（先补齐 D1-D4 事实依据，再核对阶段权重与单价口径，最后才进 `pcs-quotation`）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
# 1) 先自检（6/6 PASS）
$PY ~/.hermes/skills/mig-std/mig-app-effort/scripts/app_effort_build.py --self-test

# 2) 真实数据
$PY ~/.hermes/skills/mig-std/mig-app-effort/scripts/app_effort_build.py \
   --input examples/envision-apps.json --out-dir /tmp/ae_env
```

输入结构见文件头 docstring；`examples/envision-apps.json` 为 186 应用真实样例（源 `huawei` → 目标 `alicloud`）。
