---
name: redis-migration
description: "支持 Redis 4.x–7.x 各版本到阿里云 Redis / Tair 的迁移，涵盖全量迁移、增量同步、双向同步、在线 / 离线方案选型、跨账号迁移、大 Key 处理、版本兼容性评估。"
description_zh: "Redis 数据库迁移到阿里云"
description_en: "Redis migration to Alibaba Cloud"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
trigger: ["redis迁移", "redis sync", "redis搬迁", "tair迁移", "云数据库redis", "redis online migration"]
---

# Redis 迁移

把 Redis（含自建、AWS ElastiCache、Azure Cache）迁移到阿里云 Redis / Tair，覆盖从版本评估到双写切流的完整路径。

## 支持的目标形态

- **阿里云 Redis 社区版**：兼容 Redis 4.x–7.x
- **阿里云 Redis 企业版（Tair）**：性能增强版、持久内存版
- **自建 Redis Cluster → 阿里云 Redis Cluster**：分片结构保持

## 工作流

### 第 1 步 源端盘点

-  Redis 版本（`INFO server` 输出）
-  部署模式：单机 / 主从 / Sentinel / Cluster
-  数据规模：总 key 数、大 Key（>1MB）、热 Key
-  内存使用峰值与 QPS（按读写分别）

### 第 2 步 目标选型

| 源 | 推荐目标 |
| --- | --- |
| 自建 Redis 4.x–6.x | Redis 社区版（兼容性最好） |
| 自建 Redis 7.x | Redis 社区版 / Tair 性能增强版 |
| ElastiCache for Redis | Tair 持久内存版（成本更优） |
| Azure Cache for Redis | Redis 社区版 |

规格按 QPS 与内存选择，分片数 ≥ 源端 cluster 分片数。

### 第 3 步 迁移方案选型

| 方案 | 适用场景 | 停机时间 |
| --- | --- | --- |
| **全量 RDB 导入** | 数据 < 50 GB、可短暂停写 | 分钟级 |
| **DTS 双向同步** | 大数据量 / 不允许长时间停写 | 秒级（最终切换） |
| **redis-cli + aof 追加** | 自建到阿里云 | 分钟级 |
| **阿里云 DTS（Redis-Shake 模式）** | 跨云 / 跨账号 | 秒级 |

### 第 4 步 兼容性评估

源 Redis 版本与目标版本的兼容性：

- Redis 6+ 多线程配置 → Tair 性能增强版
- Redis 7+ Function / Sharded PubSub → 确认目标版本支持
- 自定义 LUA 脚本 → 检查目标引擎是否兼容（部分 Lua 函数差异）
- 大 Key（> 1MB） → 评估目标版规格上限，必要时拆分

### 第 5 步 双写与切流

```
阶段 1：阿里云 Redis 实例开通，配置 DTS 同步（源 → 目标）
阶段 2：观察同步延迟与数据一致性
阶段 3：应用层开启双写（写源 + 写目标）
阶段 4：逐步放量应用读目标，确认读一致性
阶段 5：完成切流，停写源端，DTS 反向同步保留回滚窗口
阶段 6：观察稳定后关闭 DTS，回收源端
```

### 第 6 步 校验

```
- 全量 key 数对比：INFO keyspace
- 抽样比对（推荐 0.1% key，hash + 字段对比）
- 监控读写 QPS / 延迟 / 命中率是否与源端一致
- 业务侧端到端验证（建议保留旧连接 24h 观察）
```

## 输出交付物

| 文件 | 说明 |
| --- | --- |
| 迁移方案书 | Markdown（含阶段、停机时间、回滚方案） |
| 兼容性评估表 | Excel |
| 切流操作 Runbook | Markdown（含命令与回滚步骤） |
| 校验报告 | Markdown（key 数、抽样结果、监控截图） |

## 边界

- **不做**：跨 Redis 版本的协议代理改造。
- **依赖**：源端需有 `replicaof` / `PSYNC` 能力；Cluster 模式需源端开启 `protected-mode no` 或配置白名单。
- **大 Key 风险**：>10 MB 的 Key 在 DTS 同步时可能阻塞，需先拆分。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 查询阿里云 Redis/Tair 实例与 DTS 任务 | `aliyun r-kvstore DescribeInstances`；DTS operation 先 `aliyun dts --help` 确认；创建/修改任务属变更，先 preview 并请求确认 |
| aliyun ossutil | 大 Key 导出经 OSS 中转 | `aliyun ossutil cp`，命令保持可复制可审查 |
