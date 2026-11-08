# {{客户名}} {{项目名}} 详细架构设计（LLD）（Azure浅蓝）

> 色系皮肤：`--brand azure`（渲染时由 `scripts/build_docx.py` 套用 Microsoft Azure 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 密级：L2-内部级
> 目标云：**Microsoft Azure** ｜ 目标地域：{{region}}
> 前置：本文件的输入是 HLD（未产出 HLD 时不得启动，参数无法落地）
> 参考域名基线：Microsoft Azure｜账号：Management Group 层次 + Subscription 划分；Az…｜网络：Virtual Network + Subnet 分层；vWAN / Expre…

---

## 1. 网络拓扑与地址规划

**1.1 地址规划表**

| VPC / VNet | 网段 CIDR | 用途 | 子网 CIDR | 可用区 | 说明 |
|---|---|---|---|---|---|
| {{名称}} | {{10.x.0.0/16}} | {{生产/测试/共享}} | {{10.x.1.0/24}} | {{az-a}} | |

**1.2 路由表**：{{每条写：目标网段 → 下一跳 → 说明}}
**1.3 互联**：{{专线 / VPN / 云联网，按 Microsoft Azure 服务实现}}
**1.4 安全组 / 防火墙规则矩阵**

| 源 | 目的 | 端口 | 协议 | 动作 | 依据 |
|---|---|---|---|---|---|

> 规则必须有依据列；写「全通 / 0.0.0.0/0 全放」须注明甲方书面确认。

## 2. 计算实例规格表

| 主机名 | 用途 | 实例规格 | vCPU | 内存 | 系统盘 | 数据盘 | 数量 |
|---|---|---|---|---|---|---|---|
| {{}} | | {{按目标地域实际可购买清单}} | | | | | |

> **规格真实性红线**：VM 规格族与数据库型号须按目标 Region 实际可购买清单复核

## 3. 数据库规格表

| 实例名 | 引擎与版本 | 规格 | 存储 | 高可用 | 备份策略 | 备注 |
|---|---|---|---|---|---|---|

## 4. 存储设计

| 存储类型 | 容量 | 访问模式 | 生命周期 | 加密 |
|---|---|---|---|---|

> 参考基线（Microsoft Azure）：Blob（Hot / Cool / Archive）；Managed Disk（Premium SSD / Ultra）；Azure Files；生命周期管理

## 5. 安全与合规清单

| # | 检查项 | 基线要求 | 当前状态 | 责任人 |
|---|---|---|---|---|

> 参考基线（Microsoft Azure）：Microsoft Defender for Cloud；Sentinel；Key Vault；DDoS Protection；Azure Policy 合规基线；合规管理器映射（由甲方确定适用项）
> 身份与访问：Entra ID（原 Azure AD）；RBAC 角色分配；PIM 特权身份管理；Managed Identity；Conditional Access

## 6. 监控与告警配置

| 监控对象 | 指标 / 日志源 | 阈值 | 告警级别 | 通知方式 |
|---|---|---|---|---|

> 参考基线（Microsoft Azure）：Azure Monitor + Log Analytics + Application Insights；Action Group / Alert Rule；备份与 Site Recovery

## 7. 部署步骤（IaC）

- 编排工具：**Bicep / ARM 模板或 Terraform（AzureRM Provider）**
- 目录结构：{{modules / environments / variables}}
- 执行顺序：{{网络 → 安全 → 计算 → 数据 → 监控}}
- 回滚方式：{{按栈销毁 / 版本回退}}

> 部署步骤里的资源规格必须人工核对是否真实存在（模板值与 Mock 值常见）。

## 8. 待确认清单

- [ ] 网段与甲方现网是否冲突
- [ ] 实例规格在目标地域的可购买性
- [ ] 数据库版本兼容性
- [ ] 安全规则例外项

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
