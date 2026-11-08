# {{客户名}} {{项目名}} 高级架构设计（HLD）（Azure浅蓝）

> 色系皮肤：`--brand azure`（渲染时由 `scripts/build_docx.py` 套用 Microsoft Azure 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 密级：L2-内部级
> 目标云：**Microsoft Azure** ｜ 状态：{{draft|final}}
> 输入事实源：`pcs-factsheet` 结构化 facts（目标云未定时先走 `pcs-arch-selection`）

---

## 0. 设计原则与总体架构

**0.1 设计原则**：{{≤6 条，每条一句话，禁止排比堆砌}}
**0.2 总体架构**：{{一段话叙述：源端 → 目标端的分区与关键路径}}
**0.3 领域覆盖一览**

| # | 领域 | 章节 | 设计结论（一句话） |
|---|---|---|---|
| 1 | 账号与组织架构 | 见 {{第1章}} | {{设计要点}} |
| 2 | 网络架构 | 见 {{第2章}} | {{设计要点}} |
| 3 | 安全与合规 | 见 {{第3章}} | {{设计要点}} |
| 4 | 身份与访问（IAM） | 见 {{第4章}} | {{设计要点}} |
| 5 | 计算 | 见 {{第5章}} | {{设计要点}} |
| 6 | 存储 | 见 {{第6章}} | {{设计要点}} |
| 7 | 数据库 | 见 {{第7章}} | {{设计要点}} |
| 8 | 监控与运维 | 见 {{第8章}} | {{设计要点}} |

> 8 大领域一一对应 `pcs-hld` 判据；任一领域留空即为未完成。

## 1. 账号与组织架构

**1.1 设计要点**：Management Group 层次 + Subscription 划分；Azure Policy 与蓝图做基线护栏；RBAC 继承设计；计费账户（EA / MCA）与成本分摊标签

**1.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**1.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**1.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 2. 网络架构

**2.1 设计要点**：Virtual Network + Subnet 分层；vWAN / ExpressRoute 做多地域与混合互联；VPN Gateway 冗余；Azure Firewall；Application Gateway；NSG / ASG；Private Link

**2.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**2.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**2.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 3. 安全与合规

**3.1 设计要点**：Microsoft Defender for Cloud；Sentinel；Key Vault；DDoS Protection；Azure Policy 合规基线；合规管理器映射（由甲方确定适用项）

**3.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**3.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**3.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 4. 身份与访问（IAM）

**4.1 设计要点**：Entra ID（原 Azure AD）；RBAC 角色分配；PIM 特权身份管理；Managed Identity；Conditional Access

**4.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**4.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**4.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 5. 计算

**5.1 设计要点**：VM / Virtual Machine Scale Sets，规格族（D / E / F 系列）；AKS；App Service；可用性区与可用性集

**5.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**5.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**5.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 6. 存储

**6.1 设计要点**：Blob（Hot / Cool / Archive）；Managed Disk（Premium SSD / Ultra）；Azure Files；生命周期管理

**6.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**6.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**6.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 7. 数据库

**7.1 设计要点**：Azure SQL / SQL Managed Instance；Azure Database for MySQL / PostgreSQL；Cosmos DB；Azure Database Migration Service（DMS）

**7.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**7.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**7.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 8. 监控与运维

**8.1 设计要点**：Azure Monitor + Log Analytics + Application Insights；Action Group / Alert Rule；备份与 Site Recovery

**8.2 关键组件**：{{按 Microsoft Azure 官方服务名填写}}

**8.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**8.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 9. 高可用与容灾

**9.1 可用性目标**：{{SLA / RTO / RPO，未确认写「待确认」}}
**9.2 容灾策略**：{{同城多 AZ / 异地灾备，按 Microsoft Azure 服务实现}}

## 10. 成本与优化

**10.1 资源清单与费用估算**：{{引用 mig-sizeng-advice / pcs-lz-estimate 输出}}
**10.2 优化建议**：{{预留实例 / 存储分层 / 闲置回收}}

## 11. 待确认清单

- [ ] 目标地域与可用区
- [ ] 合规框架（等保 / ISO27001 / SOC2 等）
- [ ] 网络互联方式与带宽
- [ ] 数据与驻留要求

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
