# Multi-Cloud Target Version Compatibility Risk Reference (目标感知)

> Last updated: 2026-11-06
> Purpose: 本文件是 `version-risks.md` 的多云目标扩展。原 `version-risks.md` 给出「源版本 vs 阿里云最低可选版本」的红线；本文件把同一规则泛化到「目标云 = 非阿里云」的场景，给出各目标云已知的最低可选版本 / 红线，供迁云调研报告做版本兼容性风险判定。
> 阿里云 作为目标时，一律使用原 `version-risks.md`，本文件不重复。
> 各云最低可选版本会随产品线演进变化，始终以各云最新官方文档为准；下表为调研判定的常用红线汇总。

---

## 通用判定规则（目标感知）

1. **提取源版本**：从调研材料中识别组件名与版本号。
2. **对照目标云最低可选版本**：用本文件的「目标云最低可选版本」表格，而不是阿里云标准。
3. **标注风险等级**：
   - 🔴 高风险：源版本低于目标云最低可选版本，必须升级。
   - 🟡 中风险：目标云支持但版本过旧，建议升级。
   - 🟢 低风险/无风险：版本兼容。
4. **记录升级路径**：对需升级项，描述升级路径与注意事项。
5. **推荐验证工具**：跨云数据库升级建议用流量回放（go-replay/tcpcopy）或各云兼容性评估工具（如 OCI Zero-Downtime Migration、AWS SCT/DMS、Azure DMS、GCP Database Migration Service、华为 数据复制服务）做验证。

---

## 各目标云最低可选版本 / 红线汇总

> 说明：M = MySQL，PG = PostgreSQL，K8s = Kubernetes。下表为常见组件的「目标云最低可选版本」，低于该值即 🔴。

### 1. 数据库

| 组件 | AWS（RDS/DocDB） | Azure（DB for MySQL/PG） | GCP（Cloud SQL） | 华为云 RDS | 腾讯云 CDB | OCI DB System |
|------|------------------|---------------------------|------------------|------------|------------|----------------|
| MySQL 最低可选 | 5.7（RDS MySQL） | 5.7 | 5.7 | 5.6 | 5.6 | 8.0 / 8.4（MySQL HeatWave） |
| MySQL 红线 | < 5.6 不支持 | < 5.6 不支持 | < 5.6 不支持 | < 5.6 不支持 | < 5.6 不支持 | OCI MySQL 默认 8.x，5.7 需自建 |
| PostgreSQL 最低可选 | 11（RDS PG） | 11 | 13 | 9.6（已接近 EOL，建议 ≥12） | — | 13 / 15 / 16 |
| PostgreSQL 红线 | < 9.6 不支持 | < 9.6 不支持 | < 11 不支持 | < 9.6 不支持 | — | — |
| SQL Server 最低可选 | 2012 | 2012（SQL Managed Instance 2014+） | — | — | — | 通过市场镜像（2019/2022） |
| Redis 最低可选 | 5.0.0（ElastiCache） | 4.0（Azure Cache） | 5.0（Memorystore） | 4.0（DCS） | 2.8/4.0（云 Redis） | 7.0（托管 Redis，旧版自建） |
| Redis 红线 | < 3.2 不支持 | < 2.8 不支持 | < 4.0 不支持 | < 3.0 不支持 | < 2.8 不支持 | 跨大版本（4→7）需评估 |
| MongoDB 最低可选 | 3.6（DocDB，兼容 4.0/5.0 API） | 4.0（Cosmos Mongo API） | — | 3.4（DDS） | 3.0/3.2 已停售 | 通过市场镜像（4.2/4.4/5.0） |
| MongoDB 红线 | < 3.2 不支持 | < 3.2 不支持 | — | < 3.0 不支持 | < 3.0 不支持 | — |

### 2. 容器 / Kubernetes

| 目标云 | 托管 K8s 服务 | 支持的最低 / 默认版本 | 红线 |
|--------|--------------|------------------------|------|
| AWS EKS | 1.29+（持续淘汰旧版），支持 1.30/1.31 | < 1.23 已不支持 | 1.22 以下 API 大量废弃（extensions/v1beta1 等） |
| Azure AKS | 1.29+ | < 1.24 不支持 | 1.25 移除 PodSecurityPolicy；CSI 迁移 |
| GCP GKE | 1.29+（常态支持 1.30/1.31） | < 1.26 不支持 | 1.22 之后弃用大量 beta API |
| 华为云 CCE | 1.25+（部分 1.23） | < 1.21 不支持 | 1.21 移除某些废弃 API |
| 腾讯云 TKE | 1.24+ | < 1.20 不支持 | 1.16 之后大量废弃 |
| OCI OKE | 1.20 ~ 1.32 | 1.20 最低受支持 | 1.19 及以下不支持；注意 CNI/CSI 版本 |
| IDC（自建） | 自定 | 视发行版 | 建议 ≥ 1.24 以获得安全补丁 |

### 3. 中间件

| 组件 | AWS | Azure | GCP | 华为云 | 腾讯云 | OCI |
|------|-----|-------|-----|--------|--------|-----|
| Kafka | MSK 2.8+（3.x 推荐） | Event Hubs Kafka 1.0+ 协议 | Pub/Sub | DMS Kafka 2.x/3.x | CKafka 2.x/3.x | Streaming 兼容 Kafka 3.x API |
| Kafka 红线 | < 0.11 协议不兼容 | — | — | < 0.10 不兼容 | < 0.10 不兼容 | 旧协议需升级 |
| RabbitMQ | Amazon MQ 3.11+ | — | — | DMS RabbitMQ 3.x | TDMQ RabbitMQ 3.x | 市场镜像 3.x |
| RocketMQ | — | — | — | DMS RocketMQ 4.x/5.x | TDMQ RocketMQ 4.x/5.x | 市场镜像 5.x |

### 4. 微服务组件

| 组件 | 跨云通用红线 | 备注 |
|------|--------------|------|
| Nacos | ≥ 1.4（推荐 2.x） | 1.x 与 2.x 协议不兼容，升级需双注册过渡 |
| ZooKeeper | ≥ 3.5（推荐 3.8） | 3.4 已 EOL |
| XXL-JOB | ≥ 2.3 | 注意调度中心与执行器版本匹配 |

---

## 报告中的标注格式（与 version-risks.md 共用）

在「资源明细」表的「迁移说明」列，凡涉及版本变化的条目，按以下格式标注：

```
[Version upgrade] 源版本 X.Y → 目标云最低/推荐版本 A.B
Risk level: High/Medium/Low
Impact: （具体差异，如 SQL 语法、API 废弃、协议变更）
Validation plan: （推荐工具与方法，如流量回放 / 目标云兼容性评估工具）
```

> 注意：目标云 ≠ 阿里云时，把 `version-risks.md` 中的「阿里云最低可选版本」整体替换为「本文件对应目标云的红线」再判定。
