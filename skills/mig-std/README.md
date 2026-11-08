# mig-std — 迁移交付 Skill 集（本地标准目录）

按 axon SKILL 规范（`SKILL-specification`）组织。gitlab 仓库：
`https://gitlab.anchnet.com/smartops_ai/msp-cap/migration`

> **2026-10-31 去重合并（Plan A，已收尾）**：售前重复项已收敛到 `presales/pcs-*`，本目录只保留
> **交付/实施向**能力。原 `migration/` 下的 12 个售前软链（mig-architecture / factsheet / hld /
> meeting-minutes / presales-architect / presales-orch / quotation / risk-register / sow /
> wbs-bigdata / wbs-migration / wbs-std）已删除，对应能力走 `presales/pcs-*`（前缀 `pcs-`）。
>
> **交付链已全部并入本目录**：`mig-cutover-plan` / `mig-cutover-wave` / `mig-datasync` / `mig-lld`（软链）
> 与 `mig-survey-table` / `mig-sizing-advice` / `mig-app-effort` / `mig-quick-estimate` /
> `mig-acceptance` / `mig-retro`（实体目录）均从 `migration/` 迁入，**`~/.hermes/skills/migration/` 目录已删除**。
> 本目录现为**迁移交付唯一入口**，共 16 个 skill。

## 目录约定

命名前缀 `mig-`；一个 skill = 一个可独立触发的过程，有明确触发条件与完成判据。

## Skill 清单

### 一、自建能力（本目录实体文件）

| name | 阶段 | 说明 |
|---|---|---|
| `mig-startup-orch` | 编排 | 项目启动唯一入口，路由与升级汇聚 |
| `mig-project-intake` | 项目启动 | 项目信息表 |
| `mig-resource-assessment` | 项目启动 | 资源评估（依赖 mig-cloud-adapter） |
| `mig-sow-generator` | 项目启动 | SOW 14 章 + `build_docx.py` |
| `mig-quotation` | 项目启动 | **离线兜底**报价；4 个本地脚本 |
| `mig-cloud-adapter` | 支撑层 | 采集能力层（贾泽鹏） |

### 二、软链进来的交付向 skill（源码 `/data/skills-src/axon-skills/migration/`）

| name | 阶段 | 说明 |
|---|---|---|
| `mig-cutover-plan` | 方案设计 | 割接方案 |
| `mig-cutover-wave` | 方案设计 | 割接批次编排 |
| `mig-datasync` | 方案设计 | 数据同步（12 迁移任务口径） |
| `mig-lld` | 方案设计 | 低阶设计（LLD） |

> 软链方式而非拷贝：源码单点维护，避免「改一处忘另一处」。

### 三、从 `migration/` 迁入的实施阶段 skill（本目录实体文件）

| name | 阶段 | 说明 |
|---|---|---|
| `mig-survey-table` | 02 调研 | 双语调研表 + 初步问题 15 条 |
| `mig-quick-estimate` | 03 选型 | 第一次调研快速粗估（人天/周期/成本区间） |
| `mig-sizing-advice` | 03 选型 | 源端资源 → 目标云规格档位折算 |
| `mig-app-effort` | 03 选型 | 应用级工作量引擎（四维度 → L1-L5 → 人天） |
| `mig-acceptance` | 05 验收 | UAT 用例清单 + 验收报告 |
| `mig-retro` | 06 复盘 | 复盘报告 + 知识库回写清单 |

> 这 6 个是实体目录（源码不在 `/data/skills-src/`），以 `mv` 迁入，非软链。
> 备份：`~/.hermes/skills-backup-20261031-mig6-143253/`

## 路由边界（避免抢话）

| 用户说 | 走 |
|---|---|
| 出 Fact Sheet / 事实清单 | `presales/pcs-factsheet` |
| 出报价单 / 算人天 | `presales/pcs-quotation`（不可达时降级 `mig-std/mig-quotation`） |
| 出 SOW / 工作说明书 | `presales/pcs-sow` |
| 出 WBS / 排期 | `presales/pcs-wbs-{std,migration,bigdata}` |
| 出 HLD / 架构选型 / 6R | `presales/pcs-hld` / `pcs-arch-selection` / `pcs-arch-6r` |
| 出风险登记册 | `presales/pcs-risk-register` |
| 出割接方案 / 批次 / 数据同步 / LLD | **本目录** `mig-cutover-plan` / `mig-cutover-wave` / `mig-datasync` / `mig-lld` |
| 出调研表 / 第一次调研 | **本目录** `mig-survey-table` |
| 快速粗估人天与价格范围 | **本目录** `mig-quick-estimate` |
| 出目标云规格选型建议 | **本目录** `mig-sizing-advice` |
| 应用级工作量 / L1-L5 评级 | **本目录** `mig-app-effort` |
| 出 UAT 用例 / 验收报告 | **本目录** `mig-acceptance` |
| 项目复盘 / 经验教训回写 | **本目录** `mig-retro` |

## 流水线

```
presales/pcs-*  ← 售前阶段（Fact Sheet → 报价 → WBS → SOW → 风险）
       │ 中标
mig-startup-orch  ← 交付阶段唯一入口
       │
mig-project-intake
    ↓ 项目信息表
mig-resource-assessment   ← mig-cloud-adapter
    ↓ 评估报告
    ├→ mig-quotation   → 报价单 + 人天
    └→ mig-sow-generator → SOW（14 章）
                              ↓
mig-lld / mig-datasync → mig-cutover-plan → mig-cutover-wave
    ↓
mig-acceptance（05 验收） → mig-retro（06 复盘）
```

调研/选型阶段（中标后、方案设计前）：

```
mig-survey-table（02 调研）
    ↓
mig-quick-estimate / mig-sizing-advice / mig-app-effort（03 选型）
    ↓
（进入上面的方案设计 → 割接 → 验收 → 复盘）
```

## 脚本合并（2026-10-31）

`mig-quotation/scripts/` 4 个实测脚本已软链进 `presales/pcs-quotation/scripts/`，
`mig-sow-generator/scripts/build_docx.py` 已软链进 `presales/pcs-sow/scripts/`：

```
pcs-quotation/scripts/ac_mig_pricing.py   ← 实体（AICC 降级本地计算）
pcs-quotation/scripts/calc_total.py       → mig-std 软链
pcs-quotation/scripts/validate_pricing.py → mig-std 软链
pcs-quotation/scripts/validate_quote.py   → mig-std 软链
pcs-quotation/scripts/xlsx_from_md.py     → mig-std 软链
pcs-sow/scripts/build_docx.py             → mig-std 软链
```

## 通用约束（所有 mig-* skill）

- **只读优先**：项目启动与调研阶段不碰变更类 API
- **输出双形态**：结构化 JSON（管线消费）+ 人类可读渲染（人读）
- **升级契约**：定义清楚什么条件下交给人，升级包含"已排除什么 / 剩余假设 / 建议先看哪里"
- **不编造**：客户名、人员、证书、案例、资源数字，未核实写"未核实"
- **零费用**：不因 skill 执行产生付费调用
- 交付物落 `~/cloud-docs/delivery/<项目>/`
