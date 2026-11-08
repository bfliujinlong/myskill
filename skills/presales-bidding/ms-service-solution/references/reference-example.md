# 参考实例：示例 Managed Service 项目（reference-only）— ms-service-solution / references/reference-example.md

> ⚠️ **本文件是参考实例，不是模板，不得照抄。**
> 这是一个**脱敏的示例项目**——用于示范 `output-template.md` 的章节结构与 `adaptation-points.md` 的适配维度如何成立。
> 下列取值是该示例项目**在各适配点上的选档结果**，仅供"一种取法长什么样"的参照。
> 新项目**必须**重新按自己的上游走一遍适配选档，**不能**默认套用示例取值。

---

## 示例项目在各适配点的选档结果

| 适配点 | 示例取值 | 当时的上游依据 |
|--------|---------|---------------|
| Run/Build 阈值 | Run ≤ N 人天 | 客户澄清 §Run/Build 定义 |
| 基础设施范围 | 混合云（公有云 ECS/DB/K8s + 自建机房若干） | RFP §资产清单 |
| Catalog 层级 | 3 层，Optional/Add-on 并入 Standard | 客户澄清 |
| SLA 项集合 | Incident/Problem/Change/可用性/DR 五组 | RFP SLA 附件 |
| SLA 严格度 | 增强档（含 Stretch 目标） | RFP SLA 附件 |
| 可用性分级 | 4 级（Mission/Business/Important/Normal） | RFP SLA 附件 |
| 治理层级 | 3 层（周 Ops / 月 Service / 季 Steer） | RFP §治理 + 澄清 |
| 语言 | 中英双语，月 Service Review 与季 Steer 英文 | RFP §全球汇报线 |
| 接管周期 | 按 RFP 允许窗口（如 6-8 周） | 接管方法论 + RFP §接管 |
| 接管阶段 | Discovery→KT→Shadow→Reverse→Go-Live+Hypercare | 素材引导表 §接管 |
| 团队规模 | Run N + Build M 人 | RFP 资源附件 |
| 服务台模式 | 7×24 集中 NOC 坐席轮班 | 客户澄清 + RFP §服务窗口 |
| 隔离度 | 完全隔离 + 固定 Build 资源池 | RFP 资源附件 |
| AI 档位 | 三级全覆盖（已有/试点/演进），人主导 | 素材引导表 §AI |
| 全球协同 | 强（双轨升级 + 全球接口对齐） | 客户澄清 |

---

## 四大证明支柱（叙事结构参照）

> 这是对"§2 方案概述—N 大支柱"的**填法示范**。支柱的**数量和主题因客户而变**，此处仅示范"支柱如何组织叙事"。

| 支柱 | 核心叙事 | 关键机制 |
|------|---------|---------|
| ① 本地可问责的统一入口 | 客户不必判断"找谁"，由 MSP 统一受理/分流/牵头闭环 | Service Catalog + Run/Build/OOS + RACI + SDM 治理 |
| ② 真实可运行的分层服务窗口 | 不是值班手机转接，是 NOC 坐席轮班 + 驻场 L2 + L3 专家池 | L1/L2/L3 分层 + War Room SOP + SLA 矩阵 |
| ③ 持续服务改进 | 不是季度念 PPT，是 Incident→Problem→CSI→Action Register→验证关闭闭环 | RCA/PIR + CAPA + 月度 Review + CSI 台账 |
| ④ 全球/本地服务集成 | 理解全球政策/工具/审批链并双向协同 | 双轨升级 + 双语 + 治理接口对齐 |

> 换个非跨国客户，支柱④可能不适用；换个纯云项目，支柱②的 NOC 表述要调整。**结构可借，取值必换。**

---

## 引用 KB 真实证据（§3.4 填法示范）

> 这是"§3.4 证据引用"的**填法示范**：每个证据类型指向 KB 中的真实素材路径。**具体材料与路径因项目而变。**

| 证据类型 | 材料（示例） | KB 来源路径（示例） |
|---------|------|------------|
| Service Catalog | China IMS Service Catalog | `03-Bidding场景素材/01-New-Bidding/原始Sample/.../Service-Catalog/` |
| SLA/SLO 矩阵 | 含计量+排除条款 | `.../SLA附件/` |
| 团队资源 | 含资质与备份 | `.../资源附件/` |
| FinOps 案例 | 真实优化明细 | `.../FinOps附件/` |
| 真实 RCA | P1 多层根因 + CAPA | `原始Sample/RCA-PIR/` |
| Transition 证据 | 接管全流程方法论 | `原始Sample/Mobilization与Transition/` |

> 新项目要引用**自己场景**在 KB `02-Offering素材/` 与 `04-脱敏案例库/` 中的对应素材，不是引用本示例的附件。

---

## 使用边界

- 本文件 reference-only，随框架发布但**不参与运行时填充**；
- skill 运行时**默认不加载本文件**，仅在需要"填法示范"时按需参照；
- 示例取值不得作为任何新项目的默认值；
- 本文件内容外发前须脱敏（此处已为脱敏骨架，无客户机密数值）。
