---
name: oss-realtime-migration
description: "基于阿里云数据传输服务 DTS / DataX / 自建反向代理，实现对象存储与关系型数据库的实时数据同步。覆盖 OSS → OSS、OSS → Data Lake、跨云实时同步、断点续传、冲突解决。"
description_zh: "对象存储实时同步与持续数据集成"
description_en: "Realtime object storage sync"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
trigger: ["实时同步", "OSS同步", "实时迁移", "realtime sync", "cdc", "data integration"]
---

# 对象存储实时同步

源端对象持续写入时，目标端保持准实时同步（延迟秒级到分钟级），适用于业务切流期、跨云双活、数据备份、容灾等场景。

## 同步模式

| 模式 | 延迟 | 适用 |
| --- | --- | --- |
| **事件触发** | 秒级 | 源端有事件通知（S3 Event / OSS Event） |
| **变更列表（List+Diff）** | 分钟级 | 数据量适中、可接受分钟级延迟 |
| **全量 + 增量轮询** | 5–30 分钟 | 数据量大、源端无事件机制 |
| **反向代理代理** | 实时 | 写源 + 写目标，应用层双写 |

## 工作流

### 第 1 步 同步方案选型

按场景：

```
源 = AWS S3，目标 = 阿里云 OSS：
  - 推荐：DTS 对象存储迁移 + EventBridge 增量触发
  - 备选：List 轮询（5 分钟间隔）

源 = 阿里云 OSS（跨地域）：
  - 推荐：OSS 跨地域复制 CRR（分钟级延迟）
  - 备选：DTS 实时同步

源 = 自建 HDFS，目标 = 阿里云 OSS：
  - 推荐：DataX / Hadoop OSS 适配器
```

### 第 2 步 配置同步任务

```yaml
源端：
  endpoint: s3.amazonaws.com
  bucket: source-bucket
  prefix: data/
  凭证：AK/SK

目标：
  endpoint: oss-cn-hangzhou.aliyuncs.com
  bucket: dest-bucket
  prefix: data/

同步规则：
  全量：一次
  增量：持续
  删除策略：不删除 / 标记删除（默认）
  大文件分片：50 MB
```

### 第 3 步 断点续传与重试

-  按对象分片记录 offset，断网/异常后从上次位置继续
-  失败对象入死信队列，单独重试
-  限速保护：源端 API 调用频率 < 阈值（默认 100 QPS）

### 第 4 步 校验与监控

```
- 同步延迟：源端 LastModified vs 目标写入时间
- 同步积压：未同步对象数（应 < 1000）
- 失败率：失败对象 / 总对象（应 < 0.01%）
- 周期性比对：每小时全量 count 对比
```

### 第 5 步 业务切流与回退

```
- 读双跑：应用读源与读目标并行，差异时报警
- 写双跑：新数据同时写入源与目标
- 切流：逐步放量读目标，确认一致后切写
- 回退预案：随时可关同步反向复制
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 实时同步方案书 | Markdown |
| 同步任务配置 | YAML / JSON |
| 监控告警配置 | Markdown |
| 切流 Runbook | Markdown |

## 边界

- **不做**：源端事件通知的开通（需客户在源云厂商控制台授权）。
- **依赖**：源端凭证、目标 Bucket 写权限。
- **冲突解决**：默认 last-write-wins；复杂冲突场景需业务层约定。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 配置与查询 DTS 同步任务 | `aliyun dts ...`（先 `aliyun dts --help` 确认 operation 与参数；创建同步任务属变更，先 preview） |
| aliyun ossutil | 对象级核对与补偿 | `ossutil ls --limited-num`、`ossutil stat` |
