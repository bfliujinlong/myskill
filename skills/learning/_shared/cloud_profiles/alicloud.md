# 阿里云 profile（主目标云）

| 字段 | 值 |
|---|---|
| **角色** | 主目标云（AGENTS.md 指定目标：OCI Always Free / 阿里云） |
| **成熟度** | ✅ 高（映射表与版本风险表齐全） |
| **识别线索** | ECS/OSS/RDS/PolarDB/MaxCompute/DataWorks/SLS/ACK；Region 形如 `cn-hangzhou`、`cn-beijing` |
| **映射参考** | `~/.hermes/skills/cloud/alibabacloud-migration-survey/references/cloud-mapping.md`（9 域） |
| **版本风险参考** | `~/.hermes/skills/cloud/alibabacloud-migration-survey/references/version-risks.md` |
| **采集日期** | 2026-05-28（随上述参考文件；变更需回来修订） |

## 8 域目标产品锚点（方案设计时的落点）

| 域 | 目标产品 | 备注 |
|---|---|---|
| 网络 | VPC / VSwitch / CEN+TR / EIP / NAT / ALB(L7) / NLB(L4) / CLB | CLB 为经典款，新建优先 ALB+NLB |
| 安全 | WAF / Anti-DDoS Pro / Cloud Firewall / Security Center / Bastionhost | — |
| IAM | RAM / KMS / SSL 证书服务 | — |
| 计算 | ECS(g/c/r/hfc/hfr/gn) / 神龙裸金属 / ECI / FC / SAE | — |
| 存储 | OSS / NAS / CPFS / OSS-HDFS / ESSD | 并行文件用 CPFS |
| 数据库 | RDS(MySQL/PG/SQLServer/MariaDB) / PolarDB(MySQL/PG/O/X) / Tair / ApsaraDB Redis / MongoDB / Lindorm / Tablestore / ADB / Hologres | Redis 选型必看 Tair 章节 |
| 大数据 | MaxCompute / DataWorks / EMR / Flink / Elasticsearch / PAI / SelectDB / ClickHouse | 数仓按离线/实时分选 |
| 监控运维 | SLS / CloudMonitor / ARMS / ActionTrail | — |

## 迁移红线（写方案时必须带）

- **Redis 源 ≤ 4.0 必须先升级**（阿里云最低 5.0）；用到扩展数据结构（exHash/TairHash）→ 选 **Tair 内存版**，磁盘版不支持任何扩展结构
- **MongoDB 最低 4.0**
- **K8s < 1.22 不支持 ACK**，须查 deprecated API（`extensions/v1beta1` Ingress → `networking.k8s.io/v1` 等）
- **容器不用 SMC**，走 YAML 重部署或 Velero 备份恢复
- **中间件选型**：事务/定时/顺序消息 → RocketMQ；日志采集/大数据管道 → Kafka；AMQP 平滑迁移 → RabbitMQ
- 数据库版本升级必须引入流量回放验证（go-replay / tcpcopy）；Oracle→PolarDB-O 先走 ADAM 评估
- 迁移工具：同质全量+增量 DTS；Oracle 异构 ADAM+DTS；Redis Redis-Shake/DTS；HBase LTS(BDS)

## 本机可用工具

- 采集：`mig-cloud-adapter`（MCP 分派，`alicloud` MCP 默认 disabled，用前开）
- 调研报告：`cloud/alibabacloud-migration-survey`（已跑通）
- 组件迁移 skill：`cloud/alibabacloud/{oss-migration,redis-migration,hdfs-migration,hive-migration,hive-metastore-migration,oss-realtime-migration,dataworks-workflow-gen,sql-to-hologres,oracle-compat-assess,ddl-compat-check,sql-compatibility-assess,network-coupling-analysis,software-coupling-analysis,migration-handbook-review,migration-plan-gen}`
