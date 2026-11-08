# GCP profile（源云 / 海外选云对比）

| 字段 | 值 |
|---|---|
| **角色** | 源云（迁出方）；在海外比价场景中作为候选目标云 |
| **成熟度** | ❌ 薄（本机仅有账单监控 skill；**无专属映射表，8 域锚点为通用知识，须实测后确权**） |
| **识别线索** | Compute Engine / GKE / Cloud Storage / Cloud SQL / BigQuery / Pub/Sub / Memorystore / Spanner / Cloud Load Balancing / Cloud Logging；Region 形如 `us-central1`、`europe-west4`、`asia-east1` |
| **映射参考** | **无本机映射表**。若需 GCP→阿里云 等价方案，先走 `cloud/cloud-migration/migration-plan-gen` 并在产物中把未确权项标「待确认」 |
| **采集日期** | 2026-10-31 |

## 8 域产品锚点（未确权，方案引用前必须实测）

| 域 | GCP 产品 | 迁阿里云常见落点（**待确认**） |
|---|---|---|
| 网络 | VPC / Subnet / Cloud VPN / Cloud Interconnect / Cloud Load Balancing / Cloud DNS / Cloud CDN | VPC / CEN+TR / ALB+NLB |
| 安全 | Cloud Armor / Security Command Center / Cloud IDS | WAF / Security Center / Cloud Firewall |
| IAM | Cloud IAM / Cloud KMS / Certificate Manager | RAM / KMS / SSL 证书 |
| 计算 | Compute Engine（MIG）/ GKE / Cloud Run / Cloud Functions | ECS / ACK / FC |
| 存储 | Cloud Storage / Persistent Disk / Filestore | OSS / ESSD / NAS |
| 数据库 | Cloud SQL / AlloyDB / Spanner / Memorystore / Firestore / Bigtable | RDS / PolarDB / Tair / Tablestore / Lindorm |
| 大数据 | BigQuery / Dataflow / Dataproc / Pub/Sub / Looker / Vertex AI | MaxCompute / ADB / Hologres / EMR / Flink / ApsaraMQ |
| 监控运维 | Cloud Logging / Cloud Monitoring / Cloud Trace / Cloud Audit Logs | SLS / CloudMonitor / ARMS / ActionTrail |

## 迁出侧要点

- **BigQuery** 无 1:1 等价：离线数仓 → MaxCompute；交互式分析 → ADB / Hologres；**SQL 方言差异需走 `ddl-compat-check` / `sql-compatibility-assess` 实测**，不得凭经验断言
- **Spanner** 为全球强一致分布式库 → Tablestore 选型的**一致性语义需重新论证**（强一致 vs 最终一致）
- **GKE** → ACK：K8s 版本 < 1.22 先查 deprecated API（见 alicloud.md 红线）
- **Pub/Sub** → ApsaraMQ：若用到事务/顺序消息则评估 RocketMQ 语义差异
- **Memorystore** → Tair/Redis：版本与扩展命令确认后再定型
- 海外比价：见 `business/multi-cloud-pricing.md`（GCP 在部分欧洲区域价格有竞争力，属 **定性判断，非报价依据**）

## 本机可用工具

- 成本/账单：`cloud/gcp-billing-monitor`、`cloud/gcp-billing-monitoring`
- 对象存储迁移：`cloud/alibabacloud/oss-migration`（支持 GCS→OSS）
- 比价：`business/cloud-pricing-tools`、`business/multi-cloud-pricing.md`
- 待建：GCP 专属映射表 + 迁移 skill（P2）
