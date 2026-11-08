# Azure profile（源云）

| 字段 | 值 |
|---|---|
| **角色** | 源云（迁出方） |
| **成熟度** | 🟡 骨架 |
| **识别线索** | VM/Blob/AKS/Files/CosmosDB/ServiceBus/EventGrid/Entra ID；Region 形如 `eastus`、`westeurope`、`japaneast`；Resource Group |
| **映射参考** | `references/cloud-mapping.md` 各表（Azure 列） |
| **采集日期** | 2026-05-28（随映射参考） |

## 8 域源端产品锚点

| 域 | Azure 源端产品 |
|---|---|
| 网络 | VNet / VNet Peering / vWAN / Public IP / Azure Firewall / Application Gateway / ExpressRoute / Azure DNS |
| 安全 | Azure WAF / DDoS Protection / Defender / Bastion |
| IAM | Entra ID(Azure AD) / Key Vault |
| 计算 | VM / App Service |
| 存储 | Blob Storage / Azure Files / Managed Disk |
| 数据库 | Azure SQL / Azure MySQL / Azure PG / Cosmos DB / Azure Cache Redis |
| 大数据 | Synapse / ADF / HDInsight / Stream Analytics / Azure Search / Azure ML |
| 监控运维 | Log Analytics / Azure Monitor / App Insights / Activity Log |

## ⚠️ 安全红线（AGENTS.md 强制）

- **Azure 监控一律 ReadOnly**，**绝不自动停资源**、不做任何写操作与生产变更
- 凭据不进聊天、文件 `chmod 600`

## 迁出侧要点

- **Cosmos DB** 多 API 形态（Mongo/SQL/Cassandra），迁移前必须确认源实际使用的 API 类型，再决定落 MongoDB / Tablestore
- **Azure SQL** → RDS SQL Server，版本 <2012 须先升级（见 version-risks.md）
- **AKS** → ACK，K8s 版本 <1.22 需查 deprecated API
- **Entra ID** → RAM，租户/租户目录结构差异需单独设计（非 1:1 映射）
