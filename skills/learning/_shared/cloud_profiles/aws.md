# AWS profile（主源云）

| 字段 | 值 |
|---|---|
| **角色** | 主源云（迁出方）；极少数场景作为目标云 |
| **成熟度** | 🟡 骨架（源端盘点口径已可用；作为目标云时参数待补） |
| **识别线索** | EC2/S3/EKS/EFS/ELB/ElastiCache/MSK/Aurora/DynamoDB/Lambda/Route53/CloudWatch；Region 形如 `us-east-1`、`eu-west-1`、`ap-northeast-1`；ARN 格式 |
| **映射参考** | `references/cloud-mapping.md` 中「Source cloud → Alibaba Cloud」各表（AWS 列） |
| **采集日期** | 2026-05-28（随映射参考） |

## 8 域源端产品锚点（盘点时按此对表）

| 域 | AWS 源端产品 |
|---|---|
| 网络 | VPC / Subnet / Transit Gateway / Elastic IP / NAT Gateway / ALB / NLB / CloudFront / Direct Connect / Route 53 |
| 安全 | AWS WAF / Shield Advanced / Network Firewall / Security Hub |
| IAM | IAM / KMS / ACM |
| 计算 | EC2（含系列规格）/ Lambda |
| 存储 | S3 / EFS / FSx for Lustre / EMR HDFS / EBS |
| 数据库 | RDS(MySQL/PG/SQLServer/MariaDB) / Aurora / ElastiCache / DocumentDB / DynamoDB / Redshift |
| 大数据 | Redshift / Athena / Glue / EMR / Kinesis / OpenSearch / SageMaker |
| 监控运维 | CloudWatch Logs / CloudWatch / X-Ray / CloudTrail |

## 迁出侧要点

- **Aurora → PolarDB** 为常见路径；版本差异须查 `version-risks.md` 的 PolarDB 章节
- **DynamoDB** 无直接等价，落 Tablestore / Lindorm，需评估数据模型改写（宽表 VS 文档）
- **ElastiCache Redis** 版本与扩展命令须确认后再选 Tair 类型（见 alicloud.md 红线）
- **MSK（Kafka）** → ApsaraMQ Kafka；若源用事务消息则改 RocketMQ，需评估语义差异
- **EMR HDFS** → OSS-HDFS / EMR，走 `cloud/alibabacloud/hdfs-migration`
- 比价素材：`/data/cloud-docs/AWSvsAliyun_Pricing_20260910.md`、`AWSvsAliyun_Quotation_20260910.xlsx`

## 本机可用工具

- 采集：`mig-cloud-adapter`（`aws` MCP 默认 disabled，用前开）
- 价格/比价：`business/cloud-pricing-tools`、`business/multi-cloud-pricing.md`
- 待建：AWS 专属迁移 skill（P2）
