---
name: hive-metastore-migration
description: "把 Hive MetaStore（元数据库）迁移到阿里云 Data Lake MetaService 或自建 MetaStore。覆盖表/分区元数据导出、UDF/SerDe 引用迁移、Hive 版本升级与兼容、跨集群 MetaStore 同步。"
description_zh: "Hive MetaStore 元数据迁移与同步"
description_en: "Hive MetaStore metadata migration"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
trigger: ["MetaStore", "Hive元数据", "MetaService", "元数据库迁移", "Data Lake Meta"]
---

# Hive MetaStore 迁移

把 Hive 的元数据库（MetaStore）迁移到阿里云 Data Lake Formation（DLF）的 MetaService 或自建 MetaStore。覆盖元数据导出、版本差异、跨集群同步。

## 工作流

### 第 1 步 源端盘点

-  MetaStore 数据库（MySQL / PostgreSQL）
-  Hive 版本（决定元数据表结构）
-  库 / 表 / 分区数量
-  自定义 UDF / SerDe 数量
-  元数据同步任务（HCatalog / 其他）

### 第 2 步 目标选型

| 场景 | 推荐目标 |
| --- | --- |
| 阿里云 Data Lake 场景 | Data Lake Formation（DLF）MetaService |
| 阿里云 MaxCompute 场景 | MaxCompute Schema |
| 混合云 / 自建 | 自建 MetaStore（MySQL/PG） |
| 跨集群同步 | 双向同步工具（如 Datacoral、阿里云 DataWorks） |

### 第 3 步 元数据导出

```
- 使用 hive-metastore 导出工具（如 Apache Atlas 集成、metastore-export）
- 输出：库、表、分区、列、UDF、SerDe、Storage Descriptor
- 排除临时表、统计信息（统计信息由目标端重新生成）
```

### 第 4 步 Schema 转换

Hive MetaStore → 阿里云 DLF/MaxCompute Schema 差异：

| Hive 概念 | DLF 对应 | MaxCompute 对应 |
| --- | --- | --- |
| Database | Database | Project / Schema |
| Table | Table | Table |
| Partition | Partition | Partition |
| Column | Column | Column |
| Storage format (ORC/Parquet) | 同 | 同 |
| SerDe | Library | Library |
| UDF | 同名注册 | 同名注册 |

### 第 5 步 数据位置映射

| 源 | 目标 | 工具 |
| --- | --- | --- |
| HDFS 路径 | OSS 路径 | 路径映射表 + DistCp |
| S3 路径 | OSS 路径 | OSS 迁移服务 |

确保 `LOCATION` 字段指向新路径。

### 第 6 步 业务验证

```
- 列出所有库表：SHOW DATABASES / SHOW TABLES
- 抽样查询：SELECT * FROM table LIMIT 10
- 元数据查询：DESCRIBE TABLE / DESCRIBE PARTITION
- UDF 调用：SELECT udf_name(column)
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 元数据导出报告 | JSON + Markdown |
| Schema 转换清单 | Excel |
| 数据位置映射表 | Excel |
| 业务验证报告 | Markdown |

## 边界

- **不做**：跨 Hive 大版本的 MetaStore Schema 升级（需先执行官方升级脚本）。
- **依赖**：源端 MetaStore 数据库访问凭证（只读权限即可）。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| alibabacloud-dataworks-metadata | 元数据查询 | 已安装 |
| aliyun-cli skill | 查询 DLF / 数据湖构建资源 | `aliyun dlf ...` 先查 help 确认 product 与 operation |
