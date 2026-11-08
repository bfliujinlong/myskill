# cloud_profiles — X 轴适配层（云差异底座）

> 用途：把所有**云厂商差异**集中在本目录，让阶段 skill（00-06）**不写 `if cloud ==`**。
> 阶段 skill 只声明 `target_cloud`，差异参数一律查本目录对应 profile。

## 文件清单

| 文件 | 云 | 角色定位 | 成熟度 |
|---|---|---|---|
| `alicloud.md` | 阿里云 | **主目标云**（AGENTS.md 指定） | ✅ 映射表齐全 |
| `aws.md` | AWS | 主源云 | 🟡 骨架（作为源云的盘点口径） |
| `azure.md` | Azure | 主源云 | 🟡 骨架（只读约束见下） |
| `huawei.md` | 华为云 | 源云 / 目标云 | 🟡 骨架 |
| `oci.md` | OCI | 目标云（Always Free） | 🟡 骨架 |
| `gcp.md` | GCP | 源云 | 🟡 骨架 |
| `multi.md` | 多云中立 | 跨云/中立场景入口 | 🟡 骨架 |

## 唯一事实源（不复制，只链接）

产品映射与版本风险的**唯一出处**是阿里云 survey 参考，**本目录不复制其内容**：

- 产品映射（9 大域）：`~/.hermes/skills/cloud/alibabacloud-migration-survey/references/cloud-mapping.md`
  - 域划分：0 识别线索 / 1 网络 / 2 数据库 / 3 中间件 / 4 微服务 / 5 计算存储 / 6 大数据 / 7 容器 / 8 安全身份 / 9 可观测
- 版本兼容风险：`~/.hermes/skills/cloud/alibabacloud-migration-survey/references/version-risks.md`
  - 含 RDS MySQL/PG/SQL Server、PolarDB、Redis/Tair、MongoDB、RocketMQ、RabbitMQ、MQTT、Nacos、ZK、XXL-Job、K8s

**规则**：任何 profile 里出现与上述两份文件冲突的内容，以那两份为准，并回来修订本文件。

## 域顺序（阶段 03 子域的编排顺序，全云统一）

`网络 → 安全 → IAM → 计算 → 存储 → 数据库 → 大数据 → 监控运维`

阶段 03 的方案设计要求按此顺序逐域输出，缺域必须显式写「本域不涉及 + 理由」，不得跳过。

## 维护纪律

- 新增云：复制骨架补 8 项字段，标注成熟度，不虚构产品参数
- 版本/价格类信息**必须注采集日期**，未核实写「待确认」
- 不写价格、单价、人天（与报价物理隔离）
