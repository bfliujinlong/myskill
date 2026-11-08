---
name: mig-quick-estimate
description: "第 1 次调研快速粗估：资源表（业务系统/虚拟机/K8s节点/容器/数据库）× 权重 → 规模因子 × 五维平均复杂度 → 总人天 → 五阶段拆分 → 周期周数 → 成本区间，用于给客户『大致架构 + 价格范围』。触发词：快速估算、粗估、大致架构、价格范围、第一次调研、资源表估算、V6工时评估。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段02, 粗估, 人天, 周期, 价格范围, 售前, quick-estimate, V6]
    related_skills: [mig-survey-table, mig-app-effort, mig-cloud-adapter, pcs-quotation, pcs-hld]
---

# 第 1 次调研快速粗估（阶段 02，mig-quick-estimate）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 第一次和客户聊完、手上只有**资源表**（业务系统数/虚拟机数/K8s 节点/容器实例/数据库实例）和大致技术栈，需要**当场给出大致架构与价格范围**时触发。完成判据：算出资源规模因子 → 五维平均复杂度 → 总人天 → 五阶段拆分 → 周期周数 → 三档成本区间，并列出全部待确认项。**与 `mig-app-effort` 分层**：本 skill 是**第 1 次粗估**（资源驱动、分钟级、误差大）；后者是**第 2 次深化**（应用级 D1-D4 四维度、需清单）。两者**串行不互斥**，先用本 skill 出范围，再用后者收敛。**与 `presales/pcs-quotation` 互斥**：本 skill 输出的三档区间是**内部测算参考**，对外报价/单价/折扣唯一口径为 `pcs-quotation`。 |
| **风险等级** | 低风险写（仅产出文档与计算；不执行任何生产变更、不停资源、不改客户环境） |
| **输入参数** | 必填：`project`/`source_cloud`/`target_cloud`/`resources.business_systems`（权重 10，核心驱动，缺失即无法估）；选填：`resources.vms`/`kubernetes_nodes`/`container_instances`/`databases{mysql,oracle,sqlserver,redis,mongodb}`、`complexity{technical,business,integration,security,compliance}_complexity`（1-5，缺失按中性值 3 并告警）、`rates`、`headcount`、`other_costs`、`band`（默认 ±25%）、`out_dir` |
| **依赖工具** | terminal（`scripts/quick_estimate.py`，stdlib only，无第三方依赖） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：RFP 刚到或第一次客户访谈后；客户问「大概多少钱、多久」；需要在细化调研前框定量级与可行性。
- 完成：① 资源因子逐项拆解可追溯 ② 五维复杂度有分值且标注来源（客户填写 / 默认中性）③ 总人天 + 五阶段人天 ④ 周期周数 ⑤ 低/中/高三档成本区间 ⑥ 待确认项清单齐全。

## 算法（与用户模板 V6 逐项对齐）

```
资源规模因子 = 业务系统×10 + 虚拟机×0.2 + K8s节点×0.3 + 容器实例×0.1 + 数据库实例合计×1.0
平均复杂度   = (技术 + 业务 + 集成 + 安全 + 合规) / 5        # 各维度 1-5
总人天       = Math.round(资源规模因子 × 平均复杂度)          # 已复刻 JS 舍入语义
阶段人天     = 需求调研.12 / 方案规划.18 / 实施部署.45 / 测试验证.15 / 验收交付.10
周期(周)     = ceil(总人天 / 5)
混合日成本   = Σ(角色日成本 × 人力占比)
成本区间     = (总人天 × 混合日成本 + 培训/应急/硬件) × (1 ± band)
```

常量集中在 `scripts/quick_estimate.py` 顶部 `RESOURCE_WEIGHTS`/`HOUR_RATIOS`/`DEFAULT_RATES`/`DEFAULT_HEADCOUNT`，来源为用户模板「云迁移售前工时评估系统 V6」。**改这些数字 = 改报价口径，需商务同意。**

舍入细节：`js_round()` 复刻 JS `Math.round`（`462.5 → 463`，Python 原生 `round` 会得到 462）；阶段拆分尾差统一归入占比最大的阶段，保证阶段合计 == 总人天。

## 判断逻辑（正文）

1. **输入校验**：`project`/`source_cloud`/`target_cloud` 或 `resources.business_systems` 缺失 → `rc=2` 并说明原因，**绝不猜数**（业务系统数权重 10，猜一个就全盘失真）。
2. **缺失复杂度**：未提供维度按中性值 3 计入并逐条告警（不静默填充）。
3. **越界**：复杂度非 1-5 → 告警；`band` 非 0-1 → 回退 0.25 并告警。
4. **红线**：产物正文明确标注「**非对外报价**」；不虚构资源数量、人员与案例；未核实项写「待确认」。
5. **量程提示**：本模型为**资源驱动**的线性粗估，对「少量超大系统」「重度重构」「强合规改造」会低估，须在 md 的「下一步」引导进第 2 次 `mig-app-effort` 深化。

## 输出形态

- `快速估算.md`（资源因子拆解 / 复杂度评分 / 阶段人天 / 成本区间 / 角色明细 / 告警与待确认 / 下一步）
- `quick_estimate.json`（含 `conclusion`/`warnings`/`suggested_action`，供 `mig-app-effort` 与 `pcs-quotation` 消费）

## 升级契约

触发：客户资源表完全拿不到却要求报价；复杂度全靠默认中性值（>3 个维度缺失）；用户要求本 skill 直接出**对外报价单**或合同条款；要求执行生产变更。
打包：`ruled_out`（已排除：资源数字是否经客户确认、复杂度是否有事实依据）、`remaining_hypotheses`（哪些复杂度维度用了默认值、哪些资源类型未统计）、`first_checks`（先补业务系统数与数据库实例数，再补五维复杂度事实，最后才进 `pcs-quotation`）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-quick-estimate/scripts/quick_estimate.py --self-test   # 7/7
$PY ~/.hermes/skills/mig-std/mig-quick-estimate/scripts/quick_estimate.py \
   --input examples/rfp-round1.json --out-dir /tmp/qe1
```

输入结构见 `scripts/quick_estimate.py` 文件头 docstring。
