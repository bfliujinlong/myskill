# {{客户名}} {{项目名}} 投标技术方案书（Azure浅蓝）

> 色系皮肤：`--brand azure`
> **默认口径**：正式投标以黑灰（`--brand blackgray`，禁蓝）为准；本变体仅在甲方明确指定
> Microsoft Azure 生态 / 或招标文件要求体现厂家风格时使用。

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 密级：L2-内部级
> 数字只从「客户直源 / 待商务确认」取，标源；禁止无源数字与虚构案例。

---

## 01 公司介绍与项目理解

- 1.1 公司核心资质（来源 `company_intro`，资质表 + 说明，**不得虚构证书编号**）
- 1.2 项目背景与痛点理解（客户资产规模 + 强制要求）
- 1.3 方案总体架构（组件 × RFP 对位表 + 关键口径；目标云：**Microsoft Azure**）

## 02 服务范围与责任边界

- 2.1 服务范围（项级目录映射表：服务域 × 条目数 × 角色 × 案例佐证）
- 2.2 Service Catalog 结构（四档 + 条目数）
- 2.3 Run / Build / OOS 分类处理流程
- 2.4 RACI 责任矩阵（拆甲方侧角色）
- 2.5 服务边界管理（排除项 + 范围变化走 PCR）

## 03 服务水平与运营保障

- 3.1 事件分级定义（P1-P4）
- 3.2 SLA / SLO 承诺（分项 + 定性 + 关键指标节选）
- 3.3 War Room 应急响应（启动条件 / 角色 / 执行流程）
- 3.4 事件管理（全生命周期 + 技术 / 管理升级矩阵）
- 3.5 问题管理（RCA 五步 + 三层根因 + 时限）
- 3.6 变更管理（分类 + 流程 + 度量）
- 3.7 监控与告警（工具 + 介入链路）
- 3.8 备份与 DR（DR-SLA 分级）

## 04 运营组织与服务协同

- 4.1 服务组织架构
- 4.2 团队配置（角色画像表）
- 4.3 升级路径（技术 / 管理双轨）
- 4.4 服务能力持续性（备份 / 知识 / 复盘）

## 05 Mobilization 与服务接管

- 5.1 双轨并行交接（Infra + Security）
- 5.2 里程碑（M0-M5）
- 5.3 验收门禁
- 5.4 交接时间轴
- 5.5 交接事项清单
- 5.6 Transition 风险管理

## 06 工具平台与技术方案（Microsoft Azure 专有基线）

- 6.1 工具清单（全量复用表）
- 6.2 ITSM 集成
- 6.3 告警介入链路
- 6.4 FinOps
- 6.5 AI 赋能
- 6.6 **目标云技术基线**：VM / Virtual Machine Scale Sets，规格族（D / E / F 系列）；…；IaC 工具：**Bicep / ARM 模板或 Terraform（AzureRM Provider）**

## 07 持续改进、安全与合规

- 7.1 CSI 闭环与案例（脱敏两段式，不构成本项目承诺）
- 7.2 安全合规运营（Microsoft Defender for Cloud；Sentinel；Ke…）

## 08 治理体系与报告

- 8.1 治理会议矩阵
- 8.2 报告体系

## 09 云厂商合作与持续演进

- 9.1 云厂商合作（与目标云：Microsoft Azure）
- 9.2 Landing Zone 与持续演进

## 附录 A：RFP 要求全量追溯矩阵

| 编号 | RFP 要求（摘要） | 方案章节 | 关键交付物 |
|---|---|---|---|

## 附录 B：覆盖率自检（四维）

```
In-Scope 项数 / 目录映射 / 案例佐证 / RFP 追溯率 / 叙事完整度 / 图示
```

---

## 硬约束速查

1. 数字只从「客户直源 / 待商务确认」取，标源；
2. 丰满 = 已确证事实的展开度，不引入无源数字；
3. 案例两段式；图只画已锚定条目；
4. 内部痕迹不外泄；不虚构人员 / 证书 / 案例（废标风险）。

> 门禁：对外交付前跑 `merge_chapters.py --strict [--rfp-count R]`，四维全 PASS 才可出稿；
> 再过 `doc-audit-gate`（去 AI 味 + 事实红线 + 版式色系）。

---

## 附录 E Microsoft Azure专有口径

**E.1 目标端平台基线**（专有服务名按官方写法，不臆造 / 不翻译）

| 领域 | Microsoft Azure 基线 |
|---|---|
| 账号与组织架构 | Management Group 层次 + Subscription 划分；Azure Policy 与蓝图做基线护栏；RBAC 继承设计；计费账户（EA / MCA）与成本分摊标签 |
| 网络架构 | Virtual Network + Subnet 分层；vWAN / ExpressRoute 做多地域与混合互联；VPN Gateway 冗余；Azure Firewall；Application Gateway；NSG / ASG；Private Link |
| 安全与合规 | Microsoft Defender for Cloud；Sentinel；Key Vault；DDoS Protection；Azure Policy 合规基线；合规管理器映射（由甲方确定适用项） |
| 身份与访问（IAM） | Entra ID（原 Azure AD）；RBAC 角色分配；PIM 特权身份管理；Managed Identity；Conditional Access |
| 计算 | VM / Virtual Machine Scale Sets，规格族（D / E / F 系列）；AKS；App Service；可用性区与可用性集 |
| 存储 | Blob（Hot / Cool / Archive）；Managed Disk（Premium SSD / Ultra）；Azure Files；生命周期管理 |
| 数据库 | Azure SQL / SQL Managed Instance；Azure Database for MySQL / PostgreSQL；Cosmos DB；Azure Database Migration Service（DMS） |
| 监控与运维 | Azure Monitor + Log Analytics + Application Insights；Action Group / Alert Rule；备份与 Site Recovery |

**E.2 迁移工具与方式**
- 评估与迁移：Azure Migrate（发现评估 + 服务器迁移 + 数据库迁移）
- 数据库迁移：Database Migration Service（DMS）/ Data Migration Assistant
- 数据迁移：Data Box / AzCopy / Data Factory
- IaC / 编排：Bicep / ARM 模板或 Terraform（AzureRM Provider）

**E.3 验收口径**
- 订阅与治理基线符合《Azure Landing Zone（CAF）基线》双方确认版
- 专有名词不翻译：VNet / AKS / Entra ID / ExpressRoute / Azure SQL / Log Analytics
- 合规基线由乙方提供配置项，审计结论归甲方

**E.4 商务口径**
- Azure 资源费用由甲方与微软侧 / CSP 结算，不含在本服务金额内
- 服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算依据

**E.5 色系与证据**
- `--brand azure` → 主色 `00477F`，表头底 `9CB9D8`，正文 `222222`
- 色值来源：Cabot_China_Azure_HLD.docx: 00477F x30, 000080 x24, D6DCE4 x12, 9CB9D8 x9
