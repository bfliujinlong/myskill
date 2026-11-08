# Multi-Cloud Target Product Mapping Reference (源所有云 → 目标所有云)

> Last updated: 2026-11-06
> Purpose: 本文件是 `cloud-mapping.md` 的多云目标扩展。原 `cloud-mapping.md` 已覆盖「源云识别线索」与「源云 → 阿里云」映射；本文件补充「目标云 = 非阿里云」时的目标产品选型，使 skill 支持 源所有云 → 目标所有云（双向任意组合）。
> 使用约定：先在原 `cloud-mapping.md` 用「Source Cloud Platform Identification Clues」识别源云，再用本文件按 `target_cloud` 选定目标产品，二者拼接即为 `product_mapping` 的一行（源产品, 目标产品, 迁移方式）。
> 阿里云 作为目标时，一律使用原 `cloud-mapping.md`，本文件不重复。
> 产品矩阵会随各云产品线演进变化，始终以各云最新官方文档为准。

---

## 目标云产品速查矩阵（按功能 × 目标云）

说明：列为目标云；阿里云见原 `cloud-mapping.md`。IDC 指自建/虚拟化（VMware/Hyper-V/裸金属），通常用开源或第三方方案替代托管服务。

### 网络

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 虚拟网络 | VPC | VNet | VPC | VPC | VPC | VPC | VCN | 自建 VLAN |
| 子网 | Subnet | Subnet | Subnet | Subnet | Subnet | Subnet | Subnet | — |
| 跨网互联 | VPC Peering / Transit Gateway | VNet Peering / vWAN | VPC Peering / Cloud Interconnect | VPC Peering / CC | Peering / CCN | VPC Peering | LPG / DRG | — |
| 公网 IP | Elastic IP | Public IP | External IP | EIP | EIP | EIP | OCI Public IP | 固定公网 IP |
| NAT 网关 | NAT Gateway | NAT Gateway | Cloud NAT | NAT Gateway | NAT Gateway | NAT Gateway | OCI NAT Gateway | iptables/SNAT |
| L4 负载均衡 | NLB / CLB | Load Balancer | Internal/External LB | ELB(L4) | CLB(L4) | BLB | OCI Network Load Balancer | F5 / LVS |
| L7 负载均衡 | ALB / ELB | Application Gateway | HTTP(S) LB | ELB(L7) | CLB(L7) | BLB | OCI Load Balancer(HTTP) | Nginx / HAProxy |
| CDN | CloudFront | Azure CDN / Front Door | Cloud CDN | CDN | CDN / ECDN | CDN | OCI CDN | 第三方 CDN |
| VPN | VPN Gateway | VPN Gateway | Cloud VPN | VPN Gateway | VPN Gateway | VPN Gateway | OCI IPSec VPN / DRG | 硬件 VPN |
| 专线 | Direct Connect | ExpressRoute | Partner Interconnect | Direct Connect(DC) | Direct Connect | Direct Connect | OCI FastConnect | 物理专线 |
| 公网 DNS | Route 53 | Azure DNS | Cloud DNS | DNS 解析 | DNSPod | 域名解析 | OCI DNS | BIND |
| 私有 DNS | Route 53 Resolver | Private DNS Zones | Cloud DNS Private | 内网 DNS | PrivateZone | — | OCI Private DNS | 自建 DNS |
| 全球加速 | Global Accelerator | Front Door | — | — | GAAP | — | 第三方 / WAF 边缘 | — |
| WAF | AWS WAF | Azure WAF | Cloud Armor | WAF | WAF | — | OCI WAF | 自建 WAF |
| DDoS 防护 | Shield Advanced | DDoS Protection | Cloud Armor | Anti-DDoS | 大禹 | — | OCI DDoS Protection | 硬件清洗 |
| 网络防火墙 | Network Firewall | Azure Firewall | Cloud NGFW | CFW | 安全组 | — | OCI Network Firewall | iptables / 硬件 |

### 数据库

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| MySQL | RDS MySQL / Aurora MySQL | Azure Database for MySQL | Cloud SQL MySQL | RDS MySQL | CDB MySQL | RDS MySQL | OCI MySQL DB System / HeatWave | 自建 MySQL |
| PostgreSQL | RDS PG / Aurora PG | Azure Database for PostgreSQL | Cloud SQL PG | RDS PG | — | — | OCI PostgreSQL DB System | 自建 PG |
| SQL Server | RDS SQL Server | Azure SQL | — | — | — | — | OCI（VM/市场镜像） | 自建 SQL Server |
| MariaDB | RDS MariaDB | Azure Database for MariaDB | — | — | — | — | OCI MariaDB | 自建 MariaDB |
| Oracle | RDS Custom / EC2 自建 | Azure VM 自建 | Bare Metal（Oracle） | GaussDB(for Oracle) | — | — | OCI Base Database / Exadata / Autonomous | 自建 Oracle |
| 分布式数据库 | Aurora Serverless v2 | Cosmos DB | Spanner | GaussDB(分布式) | TDSQL | — | OCI Globally Distributed DB | TiDB / OceanBase |
| Redis | ElastiCache | Azure Cache for Redis | Memorystore | DCS / GeminiDB Redis | 云 Redis | SCS | OCI Cache(托管 Redis) / 市场镜像 | 自建 Redis |
| Memcached | ElastiCache Memcached | — | Memorystore Memcached | DCS Memcached | — | — | — | 自建 Memcached |
| MongoDB | DocumentDB | Cosmos DB(Mongo API) | — | DDS | 云 MongoDB | — | OCI（市场镜像） | 自建 MongoDB |
| HBase / 宽表 | EMR HBase | HDInsight HBase | Bigtable | CloudTable | — | — | OCI NoSQL / Big Data | 自建 HBase |
| 数据仓库 | Redshift / Athena | Synapse | BigQuery | DWS | CDWPG / DLC | — | OCI Autonomous Data Warehouse | Hive / DW |
| 搜索引擎 | OpenSearch | Azure Cognitive Search | — | CSS | — | — | OCI OpenSearch（市场） | 自建 ES |

### 中间件

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| Kafka | MSK | Event Hubs（Kafka 兼容） | Pub/Sub | DMS Kafka | CKafka | — | OCI Streaming（Kafka API） | 自建 Kafka |
| RabbitMQ | Amazon MQ | — | — | DMS RabbitMQ | TDMQ RabbitMQ | — | 市场镜像 RabbitMQ | 自建 RabbitMQ |
| RocketMQ | — | — | — | DMS RocketMQ | TDMQ RocketMQ | — | 市场镜像 | 自建 RocketMQ |
| MQTT | AWS IoT Core | Azure IoT Hub | Cloud IoT Core | IoTDA | IoT Explorer | — | OCI IoT | 自建 MQTT |
| 事件总线 | EventBridge | Event Grid | Eventarc | EventGrid | EventBridge(CSB) | — | OCI Events | 自建 |

### 微服务

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 注册/配置中心 | Cloud Map / App Mesh | Azure Spring Apps | Cloud Run | CSE | TSF | — | OCI 容器 + Helm | Nacos / 自建 |
| API 网关 | API Gateway | API Management | API Gateway | APIG | API Gateway | — | OCI API Gateway | Kong / 自建 |
| 任务调度 | EventBridge / Step Functions | Logic Apps | Cloud Scheduler | — | — | — | OCI Scheduler | XXL-Job / 自建 |

### 计算 / 存储

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 虚机 | EC2 | Azure VM | GCE | ECS | CVM | BCC | OCI Compute | VMware / 物理机 |
| 对象存储 | S3 | Blob Storage | Cloud Storage | OBS | COS | BOS | OCI Object Storage | 自建 / MinIO |
| 块存储 | EBS | Managed Disks | Persistent Disk | EVS | CBS | CDS | OCI Block Volume | 本地盘 |
| 文件存储 | EFS | Azure Files | Filestore | SFS | CFS | CFS | OCI File Storage | NFS |
| 镜像仓库 | ECR | ACR | Artifact Registry | SWR | TCR | CCR | OCI Container Registry | Harbor |

### 大数据

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 批处理/计算 | EMR | HDInsight | Dataproc | MRS | EMR | — | OCI Big Data / Data Flow | 自建 Hadoop |
| 流处理 | Kinesis | Event Hubs | Dataflow | DMS Kafka | CKafka | — | OCI Streaming | Flink / 自建 |
| 数据仓库 | Redshift | Synapse | BigQuery | DWS | CDWPG / DLC | — | Autonomous DW | Hive |
| 搜索 | OpenSearch | Azure Cognitive Search | — | CSS | — | — | OpenSearch | ES |
| ML 平台 | SageMaker | Azure ML | Vertex AI | ModelArts | TI-ONE | — | OCI Data Science | 自建 |

### 容器

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 托管 K8s | EKS | AKS | GKE | CCE | TKE | CCE(百度) | OCI OKE | 自建 K8s |
| 服务网格 | App Mesh | — | Anthos Service Mesh | ASM | TCM | — | OKE + Istio | Istio |
| 镜像仓库 | ECR | ACR | Artifact Registry | SWR | TCR | CCR | OCI Container Registry | Harbor |

### 安全与身份

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| IAM | IAM | Entra ID / Azure AD | Cloud IAM | IAM | CAM | IAM | OCI IAM | LDAP / 自建 |
| 密钥管理 | KMS | Key Vault | KMS | KMS | KMS | KMS | OCI KMS | 自建 |
| WAF | AWS WAF | Azure WAF | Cloud Armor | WAF | WAF | — | OCI WAF | 自建 |
| DDoS | Shield | DDoS Protection | Cloud Armor | Anti-DDoS | 大禹 | — | OCI DDoS Protection | 硬件 |
| 堡垒机 | Systems Manager | Azure Bastion | — | 堡垒机 | 堡垒机 | — | OCI Bastion | 自建 |
| 证书 | ACM | App Service Cert | Certificate Manager | 私有 CA | 证书 | — | OCI Certificates | 自建 |

### 可观测性

| 功能 | AWS | Azure | GCP | 华为云 | 腾讯云 | 百度云 | OCI | IDC |
|------|-----|-------|-----|--------|--------|--------|-----|-----|
| 日志 | CloudWatch Logs | Azure Monitor Logs | Cloud Logging | LTS | CLS | — | OCI Logging | ELK |
| 指标 | CloudWatch | Azure Monitor | Cloud Monitoring | CES | 云监控 | — | OCI Monitoring | Prometheus |
| APM/链路追踪 | X-Ray | Application Insights | Cloud Trace | APM | APM | — | OCI APM | SkyWalking |
| 审计 | CloudTrail | Azure Activity Log | Cloud Audit Logs | CTS | CloudAudit | — | OCI Audit | 自建 |

---

## 映射使用规则（与 cloud-mapping.md 共用）

- **先识别源云**：用原 `cloud-mapping.md` 的「Source Cloud Platform Identification Clues」确定源云与源产品名。
- **再按目标选型**：本文件按 `target_cloud` 取对应列的目标产品；`target_cloud=阿里云` 时改用原 `cloud-mapping.md`。
- **`product_mapping` 组装**：每一行为 `(源产品名, 目标产品名, 迁移方式)`，源来自识别线索，目标来自本矩阵。
- **迁移方式随目标变化**：例如数据库跨云同步，AWS→目标 用 DMS，Azure→目标 用 Azure Database Migration Service，跨云通用可用 OCI Database Migration / 各云 DMS / 第三方（如 Striim、CloudEndure、Velostrata）。
- **版本红线随目标变化**：目标云的最低可选版本各不相同（见 `version-risks-multicloud.md`），务必用「目标云最低可选版本」而非阿里云标准做风险判定。
- **不要编造**：未在调研材料中给出的版本/数量/规格，一律填「待确认」，绝不在报告中虚构。
- **保密红线**：报告不得出现真实 IP、密码、AccessKey、私钥；OCI Always Free 场景注意零成本（不触发付费操作）。
