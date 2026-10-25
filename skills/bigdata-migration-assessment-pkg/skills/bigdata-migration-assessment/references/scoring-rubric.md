# D1–D4 打分标尺 + 异构迁移路径对照

## 一、打分标尺

打分必须**引用具体事实**，不得只给分不给依据。备注写法示例：
`4` ← `"Glue Catalog 9800 表 + Crawler + Athena + Lambda 实时计算，大数据组件最密集"`

### D1 架构复杂度（源端→目标端的异构程度）

| 分 | 判据 |
|---|---|
| 1 | 同构同版本，IaaS 层直接搬（EC2→CVM、自建 MySQL→自建 MySQL） |
| 2 | 同构跨版本，或托管→自建的简单替换 |
| 3 | 单一组件替换（消息队列换、对象存储换），架构形态不变 |
| 4 | 多个托管服务需替换，且存在无一一对应的能力（弹性伸缩策略、Serverless 计算） |
| 5 | 数仓 + 计算引擎 + 编排调度 整栈重构，目标端无等价托管服务 |

### D2 数据复杂度

| 分 | 判据 |
|---|---|
| 1 | 单库、百表以内、无方言差异 |
| 2 | 多库、千表以内、方言差异小 |
| 3 | TB 级、千表级，或存在中等方言差异（函数级） |
| 4 | 十 TB～PB 级，或万表级元数据，或方言差异涉及语法结构 |
| 5 | PB 级 + 万表级元数据 + SQL 方言需要整体重写 |

### D3 耦合度

| 分 | 判据 |
|---|---|
| 1 | 独立应用，无外部依赖 |
| 2 | 少量内部依赖 |
| 3 | 跨团队依赖，有对外接口 |
| 4 | 被多个平台依赖，或是调度/权限收口点 |
| 5 | 公共 SDK / 全平台依赖，改动波及所有下游 |

### D4 改造深度

| 分 | 判据 |
|---|---|
| 1 | Rehost：原样搬迁，配置微调 |
| 2 | Rehost + 少量配置改造 |
| 3 | Replatform：换底层服务，应用层少量改动 |
| 4 | 代码级改造：SDK 替换、接口重写、作业逻辑调整 |
| 5 | Refactor：SQL/UDF/作业逻辑整体重写，需重新验证业务语义 |

### 常见误判

| 误判 | 纠正 |
|---|---|
| "只是换个存储，给 1 分" | 若下游有 SDK 封装、权限模型依赖，D3 应≥4 |
| "数据量大就给 D1 高分" | 数据量是 D2，不是 D1。D1 只看架构异构度 |
| "Rehost 就给 D4=1" | 若 Rehost 后还要改连接串、改驱动、改权限，D4 至少 2 |
| 公共 SDK 给低分 | SDK 类模块 D3 恒取 5 —— 它决定所有依赖方的返工量 |

## 二、异构迁移路径对照表（AWS → 腾讯云）

| 源端 | 目标端 | 典型 D1 | 典型 D4 | 主要风险 |
|---|---|---|---|---|
| Redshift | TCHouse-D / TCHouse-P | 5 | 5 | SQL 方言、分布键/排序键模型不同、存储过程 |
| Glue Data Catalog | DLC 元数据 / WeData | 4 | 4 | 万表级元数据迁移、分区推断差异 |
| Glue Crawler | WeData 采集任务 | 4 | 4 | 无等价自动爬取能力，需改为显式建表 |
| Glue Spark Job | DLC Spark / EMR Spark | 4 | 5 | GlueContext / DynamicFrame API 无对端，需重写 |
| Athena | DLC | 4 | 4 | Presto 方言差异、查询接口重构 |
| Lambda | SCF | 3 | 4 | 运行时版本、触发器模型、冷启动差异 |
| SQS / SNS | TDMQ / CMQ | 3 | 4 | 消息语义（FIFO、可见性超时）、SDK 替换 |
| Kinesis | Oceanus / Flink | 4 | 5 | 分片模型不同，消费位点语义不同 |
| CloudWatch | CLS | 2 | 3 | 采集 Agent、告警规则需重建 |
| EC2 GPU + AutoScaling | GPU CVM + 弹性伸缩 | 4 | 4 | GPU 机型对应关系、伸缩策略语义 |
| ECS Capacity Provider | TKE 节点池 | 4 | 4 | 无一一对应，容量策略需重设计 |
| ECS / Fargate / Spot | TKE / EKS Serverless / 竞价节点池 | 4 | 4 | Task 定义→Deployment 转换、竞价中断策略 |
| S3 | COS | 2 | 2 | 量级决定工期；接口兼容度高 |
| EFS | CFS | 2 | 2 | 性能模式、挂载点差异 |
| RDS MySQL/PG | TencentDB MySQL/PG | 2 | 2 | 版本差异、参数组 |
| IAM | CAM | 3 | 3 | 策略语法不同，角色信任关系需重建 |
| EMR | EMR (腾讯云) | 2 | 2 | 组件版本对齐 |
| MSK / Kafka | CKafka | 2 | 2 | 版本与鉴权方式 |

> 表中给的是**典型值**，实际打分必须结合该模块的真实体量与耦合情况调整，并在备注中写明调整理由。

## 三、其他源端速查

| 源端 | 目标端（腾讯云） | 典型 D1/D4 |
|---|---|---|
| MaxCompute / ODPS | TCHouse-D / DLC | 5 / 5 |
| DataWorks | WeData | 4 / 4 |
| 阿里云 EMR | 腾讯云 EMR | 2 / 2 |
| Hologres | TCHouse-P | 4 / 4 |
| 自建 Hadoop/Hive | EMR / DLC | 2–3 / 2–3 |
| 自建 ClickHouse | TCHouse-C | 1–2 / 1–2 |
| Airflow / DolphinScheduler | WeData 调度 / 自建保留 | 3 / 3 |
| 自建调度平台 | 保留自建（改连接与鉴权） | 3 / 3（D3 取 4，调度是收口点） |
