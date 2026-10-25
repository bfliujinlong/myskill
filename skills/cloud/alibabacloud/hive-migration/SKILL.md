---
name: hive-migration
description: "Hive 表结构、数据、UDF 迁移到阿里云 MaxCompute / Data Lake。覆盖 HiveQL → MaxCompute SQL 转换、分区策略映射、自定义 UDF 重写、Hive MetaStore 同步。"
description_zh: "Hive 数据迁移到阿里云"
description_en: "Hive data migration to Alibaba Cloud"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
trigger: ["Hive迁移", "Hive上云", "Hive MetaStore", "HiveQL", "Hive UDF", "Hive to MaxCompute"]
---

# Hive 迁移

把 Hive 表与数据迁到阿里云 MaxCompute / 数据湖，同时处理 HiveQL 与 MaxCompute SQL 的语法差异、UDF 重写、分区策略映射。

## 工作流

### 第 1 步 源端盘点

-  Hive 版本（1.x / 2.x / 3.x）
-  元数据库（MySQL / PostgreSQL）
-  表数量（按存储格式：TextFile / ORC / Parquet）
-  分区表占比、外部表占比
-  自定义 UDF / SerDe 数量

### 第 2 步 表结构转换

HiveQL → MaxCompute SQL 主要差异：

| HiveQL | MaxCompute SQL | 说明 |
| --- | --- | --- |
| `STRING` | `STRING` | 一致 |
| `MAP<STRING,STRING>` | `MAP<STRING,STRING>` | 一致 |
| `STRUCT<...>` | `STRUCT<...>` | 一致 |
| `ARRAY<...>` | `ARRAY<...>` | 一致 |
| `PARTITIONED BY` | `PARTITIONED BY` | 一致 |
| `STORED AS ORC` | `STORED AS ORC` | 一致 |
| `CLUSTERED BY ... INTO N BUCKETS` | 不支持 | 改用分桶表 + Range/Hash 分区 |

### 第 3 步 UDF 重写

| UDF 类型 | 处理 |
| --- | --- |
| 内置 Hive UDF | 大部分 MaxCompute 兼容，少量需替换 |
| 自定义 Java UDF | 重写为 MaxCompute UDF（注意：依赖 jar 需重新打包） |
| Python UDF | 用 MaxCompute Python UDF |
| GenericUDF | 重写为 MaxCompute 自定义函数 |
| UDAF / UDTF | 重写为聚合函数 / 表值函数 |

### 第 4 步 数据迁移

-  全量：Hive 表数据导出为 ORC/Parquet → 上传 OSS → 通过 MaxCompute 外部表挂载
-  增量：Hive 增量分区 → MaxCompute 增量分区
-  实时：CDC 工具（DataWorks 数据集成）

### 第 5 步 业务切流

```
- 应用层 Hive JDBC URL 替换为 MaxCompute JDBC
- 查询语法兼容性测试
- 性能对比：Hive 执行计划 vs MaxCompute 执行计划
- 数据抽样比对
```

### 第 6 步 校验

```
- 表数、行数：源端 vs 目标
- 抽样查询：TOP 10 业务 SQL 在目标侧运行
- 性能基线：核心作业在目标侧的耗时对比
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 表结构转换报告 | Excel（逐表） |
| UDF 重写清单 | Markdown |
| 数据迁移 Runbook | Markdown |
| 切流 Runbook | Markdown |
| 校验报告 | Markdown |

## 边界

- **不做**：复杂业务 SQL 的等价改写（需要业务团队参与）。
- **依赖**：Hive MetaStore 元数据库访问权限。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| alibabacloud-dataworks-datastudio-develop | DataWorks 节点开发与部署 | 已安装；MaxCompute 作业生成与部署直接用它 |
| alibabacloud-dataworks-metadata | 表与元数据查询 | 已安装，转换前先查目标端已有表 |
| aliyun-cli skill | 查询 MaxCompute 项目信息 | `aliyun maxcompute ...` 先查 help |
