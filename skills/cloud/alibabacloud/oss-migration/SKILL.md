---
name: oss-migration
description: "把本地或 AWS S3 / Azure Blob / GCP GCS 等对象存储迁移到阿里云 OSS。覆盖全量迁移、增量同步、跨账号 / 跨地域、断点续传、传输加密、带宽控制、校验。"
description_zh: "对象存储迁移到阿里云 OSS"
description_en: "Object storage migration to Alibaba OSS"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
trigger: ["OSS迁移", "对象存储迁移", "S3迁移", "Azure Blob迁移", "GCS迁移", "data migration"]
---

# 对象存储迁移（OSS）

把源端的对象存储迁到阿里云 OSS，覆盖主流源端、跨账号/跨地域场景。配套阿里云数据传输服务（DTS）与 OSS 迁移工具。

## 支持的源端

-  AWS S3
-  Azure Blob Storage
-  Google Cloud Storage
-  自建 MinIO / Ceph
-  本地文件系统（NAS / 本地盘）
-  阿里云 OSS 跨账号 / 跨地域

## 工作流

### 第 1 步 源端盘点

-  Bucket 列表与命名
-  对象总数、总大小、文件类型分布
-  对象命名规范（是否有前缀分层）
-  历史访问模式（热/冷/归档）

### 第 2 步 目标 OSS 规划

| 考量 | 选型 |
| --- | --- |
| 数据量 < 100 TB，频繁访问 | 标准存储 |
| 数据量 100 TB–1 PB，30 天内偶尔访问 | 低频访问 |
| 备份 / 归档，季度访问 | 归档存储 / 深度归档 |
| 跨地域容灾 | 跨地域复制（CRR） |

Bucket 命名遵循 `<业务域>-<环境>-<region>` 规范；启用版本控制防误删。

### 第 3 步 迁移方案

| 场景 | 工具 | 说明 |
| --- | --- | --- |
| < 10 TB，一次性 | ossutil / 阿里云 OSS 迁移工具 | 全量 + 校验 |
| 10 TB–1 PB | 阿里云 DTS（OSS 数据迁移） | 断点续传、增量同步 |
| > 1 PB / 跨国 | 阿里云闪电立方（线下物理介质） | 适合 TB–PB 级 |
| 跨云 API 限流 | 限速 + 多任务分片 | 避免触发源端限流 |

### 第 4 步 配置迁移任务

```
源端凭证：AccessKey / IAM Role / SAS Token
目标 Bucket：oss://<bucket>/
过滤规则：include/exclude 前缀、文件名模式
调度：低峰时段（建议 02:00–06:00）
限速：源端带宽允许的最大值
```

### 第 5 步 校验

```
- 对象总数：源端 vs 目标
- 抽样比对：MD5 / CRC64 校验和
- 关键前缀全量校验：核心数据 100% 校验
- 访问权限验证：签名 URL、ACL、生命周期规则
```

### 第 6 步 业务切流

```
- 应用层切换 endpoint（如 s3.xxx.amazonaws.com → oss-cn-hangzhou.aliyuncs.com）
- 灰度切换：10% → 50% → 100%
- 双写期观察：源端与目标同时接收写入
- 完成后清理：保留源端 7–30 天再释放
```

## 输出交付物

| 文件 | 说明 |
| --- | --- |
| 迁移方案书 | Markdown |
| 目标 OSS 规划 | Excel |
| 迁移任务配置 | JSON / 文档 |
| 校验报告 | Markdown |
| 切流 Runbook | Markdown |

## 边界

- **不做**：跨云厂商的 IAM 权限迁移（需客户账号授权）。
- **依赖**：源端 AccessKey / IAM Role 由客户提供；超大数据量需提前评估带宽窗口。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill（ossutil） | 直连 OSS 执行迁移与校验 | `aliyun ossutil ls`、`cp -r`、`sync --update`；大文件分片自带；写操作先 preview |
| aliyun-cli skill | 查询 DTS 迁移任务状态 | `aliyun dts ...` 先查 help 确认 operation |
