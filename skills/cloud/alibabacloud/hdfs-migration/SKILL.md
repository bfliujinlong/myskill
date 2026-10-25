---
name: hdfs-migration
description: "把 HDFS 上的数据迁移到阿里云 OSS / Data Lake / MaxCompute 湖仓。覆盖 DistCp / Hadoop OSS 适配器 / DataX / 闪电立方，支持分批、断点续传、压缩格式保留、权限迁移。"
description_zh: "HDFS 数据迁移到阿里云"
description_en: "HDFS data migration to Alibaba Cloud"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
trigger: ["HDFS迁移", "数据湖迁移", "DistCp", "hadoop迁移", "HDFS上云", "lakehouse迁移"]
---

# HDFS 数据迁移

把 HDFS 上的数据迁到阿里云的湖仓体系（OSS / Data Lake Formation / MaxCompute / Hologres）。覆盖离线批量与增量两种模式。

## 工作流

### 第 1 步 源端盘点

-  集群版本（CDH / HDP / EMR / 自建）
-  HDFS 总容量、文件数、目录结构
-  压缩格式：gzip / snappy / lzo / parquet / orc
-  小文件占比（< 1 MB 的文件占比）
-  数据更新频率（是否有 append / overwrite）

### 第 2 步 目标选型

| 数据特征 | 推荐目标 |
| --- | --- |
| 原始日志、文件、图片 | OSS 标准存储 |
| 结构化数据（Parquet/ORC） | MaxCompute / 数据湖 |
| 高频查询 | Hologres（列存） |
| 长期归档 | OSS 归档存储 / 深度归档 |

### 第 3 步 迁移工具选型

| 工具 | 适用 | 性能 |
| --- | --- | --- |
| **DistCp + OSS-Hadoop 适配器** | 离线批量、TB 级 | 中（受集群带宽） |
| **DataX** | 异构、需过滤转换 | 中 |
| **阿里云闪电立方** | PB 级、物理介质 | 高 |
| **OSS 数据在线迁移服务** | 已有源端 OSS 兼容 | 高 |
| **自建 Spark/Flink Job** | 复杂过滤、转换 | 取决于实现 |

### 第 4 步 离线批量迁移

```bash
# DistCp 方式
hadoop distcp \
  -D fs.oss.endpoint=oss-cn-hangzhou.aliyuncs.com \
  -D fs.oss.accessKeyId=... \
  -D fs.oss.accessKeySecret=... \
  hdfs://source/path/ \
  oss://dest-bucket/path/

# 小文件合并
hadoop distcp -strategy dynamic -m 50 hdfs://source/path/ oss://dest/path/
```

建议并发 = 集群节点数 × 2；每批次 1–10 TB。

### 第 5 步 校验

```
- 文件总数对比：源端 vs 目标
- 大小对比：累计字节数
- 抽样 CRC：Parquet/ORC footer 校验
- Schema 一致性：Parquet/ORC schema 比对
- 业务侧抽样查询验证
```

### 第 6 步 增量同步

-  监听 HDFS 新增 / 修改文件（FileSystem listener）
-  按修改时间过滤增量
-  按目录前缀分桶并行同步

### 第 7 步 权限迁移

```
- 源端 HDFS ACL → 目标 OSS 权限映射
- 命名空间映射：/user/hive/warehouse → oss://bucket/hive/
- 用户/组映射：本地用户 → RAM 子账号
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 迁移方案书 | Markdown |
| 工具命令清单 | Bash 脚本 |
| 校验报告 | Markdown |
| 权限映射表 | Excel |

## 边界

- **不做**：HDFS Kerberos 认证搭建（需客户运维配合）。
- **依赖**：源端 HDFS 服务可访问、网络带宽评估、目标 Bucket 开通。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 查询 EMR 集群与 OSS 目标 | `aliyun emr ...`（先查 help）、`aliyun ossutil ls` |
| alibabacloud-emr-cluster-manage | EMR 集群管理与操作 | 已安装，按需加载 |
