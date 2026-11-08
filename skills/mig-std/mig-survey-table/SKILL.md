---
name: mig-survey-table
description: "云迁移阶段 02 调研（第 1 次调研）：按目标云 profile 生成双语调研表（客户信息/合规安全/网络/资源清单/应用拓扑/数据库/非功能需求/云差异），供客户访谈与资源表采集。触发词：调研表、客户访谈、需求调研、资源清单采集、初步问题、第1次调研。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段02, 调研, 需求采集, 资源清单, 双语, 客户访谈, survey]
    related_skills: [mig-project-intake, mig-cloud-adapter, mig-resource-assessment, mig-app-effort, mig-quick-estimate, pcs-lz-discovery]
---

# 迁移调研表生成（阶段 02，第 1 次调研，mig-survey-table）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 拿到 RFP/客户需求后**第一次与客户聊**、需要一张表去**收资源表/拉平台数据/问清初步问题**时触发。完成判据：生成 8 个 sheet 的双语调研表（3 表单 + 4 表格 + 1 目标云差异），必填项标注 `*` 并统计填写覆盖率，输出 xlsx + md + json 三形态。**与 `mig-project-intake` 互补**：立项信息收完、进现场调研用本 skill；**与 `mig-app-effort` 串联**：本 skill 收清单 → 后者做应用级工作量估算；**与 `mig-quick-estimate` 串联**：本 skill 的资源数字 → 后者出大致架构与价格范围。**与 `pcs-quotation` 互斥**：本 skill 不产金额。 |
| **风险等级** | 低风险写（仅产出文档；**不执行任何生产变更、不停资源、不改客户环境**） |
| **输入参数** | 必填：`project`/`source_cloud`/`target_cloud`；选填：`lang`（`zh`/`en`/`bilingual`，默认 `bilingual`）、`client`（客户/项目字段预填）、`resources[]`、`systems[]`、`databases[]`、`nfr[]`、`profile_dir`、`out_dir` |
| **依赖工具** | terminal（`scripts/survey_table_build.py`，stdlib only；`openpyxl` 可选，缺失时降级为 md/json 并显式说明，不静默） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：RFP/客户需求已到、进入第一次客户访谈或资料索取；或需要用一张结构化清单去「拉平台」核对资源。
- 完成：① 8 个 sheet 齐全 **+ 初步问题 15 条已并入** ② 客户基本信息 7 个必填项已标注并统计 ③ 目标云差异 sheet 8 域锚点全部取到（profile 缺失时写「待确认」，不编造）④ 三形态产物齐全 ⑤ 未填项一律「待确认」而非示例数据。

## 判断逻辑（正文）

1. **必填校验**：`project`/`source_cloud`/`target_cloud` 缺失 → 无头模式 `rc=2`；客户基本信息 7 个 `*` 字段（客户名称/项目名称/源云/目标云/迁移类型/停机窗口/目标地域）统计填写数，缺则列入 `missing_required` 并在结论中标「不完整」。
2. **sheet 构成**：`客户基本信息`、`合规与安全`、`网络与跨云连接`（表单式）+ `资源清单`(14 列)、`应用拓扑`(10 列)、`数据库详情`(13 列)、`非功能需求`(5 列)（表格式）+ `目标云差异`。
3. **初步问题 15 条（固定问题集）**：`templates/初步问题15条.md` 为第 1 次访谈（kick-off）标准问询清单（中英双语，分 LZ架构/IaC 1–5 · 迁移范围 6–10 · 合规监管 11–14 · 超量程项 15）。生成调研表时**并入**（作为「初步问题」sheet 或访谈提纲附件），并按 `类别` 路由到对应 sheet。**高阻塞 4 题（Q5 RTO/RPO、Q10 HyperCare 回滚赔偿、Q11 等保责任、Q12 PIPL 数据处理者）必须先问**，未落定不得进入工作量估算。客户非本例项目时保留问题骨架、替换客户名与数值，**不得照抄本项目特定数字**；每题记录三列「客户原话 / 我方判读 / 待确认项」，不得合并。
4. **预填不编造**：调用方给了 `resources`/`systems`/`databases`/`nfr` 才预填；**没给就只出表头**，绝不塞示例数据（示例数据会被客户当成真实基线）。NFR 只预置**指标行**（RTO/RPO/可用性分档/灾备等级/停机窗口/备份策略），要求值留空等客户填。
5. **X 轴适配**：读 `learning/_shared/cloud_profiles/{target_cloud}.md` 取 8 域（网络/安全/IAM/计算/存储/数据库/大数据/监控运维）产品锚点，生成「目标云差异」sheet 说明源→目标的产品映射与注意点；profile 缺失 → 写「待确认」并记入 `remaining_hypotheses`。
6. **红线**：表格内**不出现价格/单价/人天/月费**（调研与报价物理隔离，xlsx 首屏已写入该声明）；不虚构资源数量、应用名、人员与案例；未核实一律「待确认」。

## 输出三形态

- `调研表_{lang}.xlsx`（含填写说明 sheet，声明本表无价格信息）
- `调研表.md`（黑灰配色口径、无蓝、去 AI 味）
- `survey_table.json`（结构化，含 `coverage`/`missing_required`，供 `mig-app-effort`/`mig-quick-estimate` 消费）

## 升级契约

触发：必填缺失且无法反问；目标云 profile 完全缺失导致差异 sheet 不可用；客户拒绝提供资源表且要求直接报价（此时应升级给商务，不得凭空估）。
打包：`ruled_out`（已排除：资源表是否经客户确认、网络拓扑是否有图）、`remaining_hypotheses`（哪些域缺 profile、哪些 NFR 未取到）、`first_checks`（先补 7 个必填，再补资源清单与数据库详情，最后才进工作量估算）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-survey-table/scripts/survey_table_build.py --self-test
$PY ~/.hermes/skills/mig-std/mig-survey-table/scripts/survey_table_build.py \
   --input input.json --out-dir ./out
```

输入结构见 `scripts/survey_table_build.py` 文件头 docstring。
