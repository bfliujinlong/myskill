# {{客户名}} {{项目名}} 迁移服务报价单（Azure浅蓝）

> 色系皮肤：`--brand azure`（渲染时由 `scripts/build_docx.py` 套用 Microsoft Azure 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 币种：{{CNY|USD}}
> 单价基准：$350/人天（AC-MIG）｜ 有效期：{{30}} 天
> 目标云：**Microsoft Azure**
> 状态：{{draft|final}}

---

## 一、计价假设

| 项 | 取值 | 来源 |
|---|---|---|
| 单价（人天） | $350 | AC-MIG 基准 |
| 目标云 | Microsoft Azure | 项目信息表 |
| 项目类型 | {{新建/迁移/改造}} | 项目信息表 |
| 复杂度系数 | {{1.0 / 1.2 / 1.5}} | 评估报告 |
| 多区域标志 | {{是/否}} | 项目信息表 |
| 异构数据库标志 | {{是/否}} | 评估报告 |
| 交付语言 | {{中/英/双语}} | 项目信息表 |

> 未确认项一律不臆造，列入「五、待确认清单」。

## 二、角色 × 人天明细

| # | 角色 | 工作内容 | 人天 | 单价 | 小计 |
|---|---|---|---|---|---|
| 1 | {{角色}} | {{内容}} | {{n}} | 350 | {{n×350}} |
| … | | | | | |
| | **合计** | | **{{总人天}}** | | **{{总金额}}** |

> 角色池：PM · 云架构师 · 云工程师（计算及存储）· 迁移工程师（中间件）· 数据库工程师 · 大数据工程师 · 安全架构师 · {{专项实施方}}团队

## 三、加计项

| 项 | 触发条件 | 加计比例 | 金额 |
|---|---|---|---|
| 多区域 | 跨 ≥2 地域 | {{}} | |
| 异构数据库 | 跨引擎迁移 | {{}} | |
| 风险储备 | 复杂度 ≥1.2 | {{}} | |

## 四、总计

| 项 | 金额 |
|---|---|
| 人天小计 | {{}} |
| 加计合计 | {{}} |
| **合同金额** | **{{}}** |

> 校验：人天 × 单价 = 小计，各行小计之和 = 总计。
> 执行 `scripts/validate_quote.py` 自动校验，失败不得出稿。

## 五、待确认清单

- [ ] RTO / RPO
- [ ] 停机窗口
- [ ] 数据增量
- [ ] 第三方 License
- [ ] 等保 / 合规要求
- [ ] 目标地域与可用区清单

## 六、不含项

- 云资源费用（由甲方与Microsoft Azure侧直接结算）
- 第三方软件 License
- 甲方人员配合成本
- 超出约定轮次的方案返工

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
