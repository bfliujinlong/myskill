# 华为云 profile（源云 / 备选目标云）

| 字段 | 值 |
|---|---|
| **角色** | 主要源云之一；政企/国产化场景也可能作为目标云 |
| **成熟度** | 🟡 骨架 |
| **识别线索** | ECS/OBS/CCE/SFS/ELB/DCS/DWS/DMS/GaussDB/SecMaster/CTS/LTS；Region 形如 `cn-north-4`、`cn-south-1`、`ap-southeast-3` |
| **映射参考** | `references/cloud-mapping.md` 各表（Huawei Cloud 列） |
| **采集日期** | 2026-05-28（随映射参考） |

## 8 域产品锚点

| 域 | 华为云产品 |
|---|---|
| 网络 | VPC / VPC Peering / CC / EIP / NAT / ELB / CFW |
| 安全 | WAF / Anti-DDoS / SecMaster / CBH |
| IAM | IAM / DEW / CCM |
| 计算 | ECS / BMS / CCE |
| 存储 | OBS / SFS / EVS / CloudTable(HBase) |
| 数据库 | RDS(MySQL/PG) / GaussDB / DCS Redis / GeminiDB Redis / DDS MongoDB |
| 大数据 | DWS / DLV / DataArts / MRS / DLI(Flink) / ModelArts |
| 监控运维 | LTS / CES / AOM / CTS |

## 迁出侧要点（高频坑）

- **GeminiDB Redis 用 exHash 扩展命令** → 必须选 **Tair 内存版**（约 27 条 TairHash 命令兼容），选磁盘版会运行时报错
- **DCS Redis / DDS MongoDB** 版本须核对最低可选型（Redis 5.0 / MongoDB 4.0）
- **GaussDB(for Oracle)** → PolarDB-O，先走 ADAM 评估
- **MRS HDFS** → OSS-HDFS / EMR；**DWS** → MaxCompute / ADB / Hologres
- **MRS/DataArts** 的调度作业迁 DataWorks 时，用 `cloud/alibabacloud/dataworks-workflow-gen`

## 本机可用工具

- 采集：`mig-cloud-adapter`（`hw*` MCP 默认 disabled，用前开）
- 待建：华为云专属迁移 skill（P2）
