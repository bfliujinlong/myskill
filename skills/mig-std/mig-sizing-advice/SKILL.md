---
name: mig-sizing-advice
description: "云迁移阶段 03 选型：把源端资源清单（vCPU/内存/存储/引擎版本/峰值利用率）折算为目标云规格档位与实例族建议，输出 sizing_advice.md + json。触发词：选型建议、规格折算、目标云规格、sizing、right-sizing、资源清单转规格。"
version: 2026-10-31.001
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [阶段03, 选型, 规格折算, sizing, right-sizing, 实例族, 双语]
    related_skills: [mig-survey-table, mig-resource-assessment, mig-quick-estimate, mig-app-effort, pcs-arch-selection, pcs-quotation]
---

# 目标云规格选型建议（阶段 03，mig-sizing-advice）

| 字段 | 值 |
|---|---|
| **description（路由用）** | 已拿到源端资源清单（含规格与峰值利用率）、且**目标云已定**，需要把资源折算成目标云规格档位（几 C 几 G / 什么实例族 / 多少容量）时触发。完成判据：逐项给出源规格→建议规格 + 实例族 + 折算假设 + 告警，缺数据项标「待确认」不臆造，输出 md + json 双形态，且**全文无金额**。**与 `mig-resource-assessment` 区别**：后者做源端采集与评估（现状盘点），本 skill 做源→目标的规格换算；**与 `pcs-arch-selection` 区别**：目标云未定时的选型/比选用后者，本 skill 在目标云已定后只做规格档位；**与 `mig-quick-estimate` 区别**：后者出人天与价格区间，本 skill 只出规格与容量；**与 `pcs-quotation` 互斥**：本 skill 绝不产金额。 |
| **风险等级** | 低风险写（仅产出文档；**不执行任何生产变更、不停资源、不改客户环境**） |
| **输入参数** | 必填：`project`/`source_cloud`/`target_cloud`/`resources[]`；资源项必填：`id` + `domain`；compute/database/cache/bigdata 域需 `vcpu`+`mem_gb`；storage 域需 `storage_gb`。选填：`growth_factor`（默认 1.2）、`peak_cpu_pct`/`peak_mem_pct`（缺失按 30% 保守假设并告警）、`os`/`engine`/`version`/`env`/`k8s_version` |
| **依赖工具** | terminal（`scripts/sizing_advice.py`，stdlib only，无第三方依赖） |
| **版本** | 2026-10-31.001 |

## 触发条件 / 完成判据

- 触发：`mig-survey-table` 的资源清单已回收（或客户直接给了资源表/云平台导出），目标云已确定，需要给架构方案配规格或给报价提供资源基线。
- 完成：① 每项资源都有「源规格 → 建议规格 + 实例族」或明确「待确认」② 折算假设（目标水位/峰值/增长系数）逐项记录 ③ EOL 与引擎最低版本告警全触发 ④ 汇总表按域统计 vCPU/内存/存储 ⑤ md + json 双形态 ⑥ **全文零金额**。

## 判断逻辑（正文）

1. **折算公式**：`有效容量 = 源规格 × (峰值利用率 / 目标水位 60%) × 增长系数(默认 1.2)`，再向上取规格档位（`LADDER`/`MEM_LADDER`）。
2. **边界钳制**：缩容 < 0.5×源、扩容 > 3×源 → 钳制并置 `needs_human_confirm`（公式越界即不可信）。
3. **方向一致性（三态 verdict）**：CPU 与内存折算方向不一致（如 8C32G → 4C64G）判为 **混合**，强制 `needs_human_confirm` 并给出原因文案（档位离散 + 源端 CPU/内存利用率不匹配），**不得直接进方案**。另：档位上取跨度 ≥2 倍时附加「保守上取，须人工复核是否可下调」提醒。
4. **实例族选定**：按目标 `内存/vCPU` 比选族 —— ≤2 计算型、≤8 通用型、>8 内存型；只输出**有事实源支撑**的实例族（alicloud/aws/huawei），其他云或未覆盖的族一律「待确认」，**绝不臆造规格名**。
5. **硬约束告警（内置，不依赖模型记忆）**：OS EOL 表（CentOS 6/7/8、RHEL 6、WS2008/2012、Ubuntu 16.04）；引擎最低版本（Redis ≥5.0 且源 ≤4.0 必升级、MongoDB ≥4.0、MySQL ≥5.7、PG ≥10、Oracle ≥12c、SQL Server ≥2016）；异构引擎（Oracle/Aurora/SQL Server）单独兼容性评估；K8s <1.22 查 deprecated API。
6. **存储域单独处理**：只算容量（×1.2），>10TB 触发超大量告警（须分阶段迁移或离线搬运，不得套在线同步）。
7. **非生产突发型**：`env=nonprod` 且峰值 CPU <40% 才标 `burst_eligible`；生产一律不用突发型（CPU 积分耗尽掉性能）。
8. **红线**：① **不输出任何金额/单价/月费**（选型与报价物理隔离，文末写口径声明）；② 缺源规格/未知云/未知实例族 → 一律「待确认」，禁止凭空给档位；③ 不虚构客户资源与应用名。

## 输出双形态

- `sizing_advice.md`：汇总（按域）+ 逐项明细（源→目标/实例族/建议规格/假设/告警/人工确认标记）+ 需人工确认清单 + 待确认清单 + 无价格声明。
- `sizing_advice.json`：结构化，含 `items[]`/`total`/`todo`/`needs_human_confirm`，供 `mig-quick-estimate` 与 `pcs-arch-selection` 消费。

## 升级契约

触发：`needs_human_confirm` 项占比 >30%（说明源端数据质量不足，公式不可信）；目标云无实例族事实表且客户要求给具体规格名；客户要求本产物直接带价格（应转 `pcs-quotation`，不得就地估价）。
打包：`ruled_out`（源端峰值利用率是否实测、目标水位是否客户认可）、`remaining_hypotheses`（缺 `peak_*` 而走默认值的项、缺源规格的项）、`first_checks`（先补实测峰值利用率与缺失规格，再复核全部「混合」项，最后才进报价/方案）。

## 用法

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
$PY ~/.hermes/skills/mig-std/mig-sizing-advice/scripts/sizing_advice.py --self-test
$PY ~/.hermes/skills/mig-std/mig-sizing-advice/scripts/sizing_advice.py \
   --input examples/customer-round1.json --out-dir ./out
```

输入结构见 `scripts/sizing_advice.py` 文件头 docstring；`examples/customer-round1.json` 为真实客户样例（9 项，含 Oracle 11.2 / MySQL 5.6 / Redis 3.2 / 25TB NAS / 缺规格项）。
