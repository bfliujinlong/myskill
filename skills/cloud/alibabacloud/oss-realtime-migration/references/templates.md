# 输出模板：对象存储实时同步

`<>` 为占位符，产出时替换。

## 模板 1：同步方案书

```markdown
# 对象存储实时同步方案

- 源端：<AWS S3>，增量写入 <X> 万对象/天
- 目标：<阿里云 OSS>
- 同步模式：<事件触发（EventBridge）+ DTS 兜底轮询>
- 目标延迟：<P99 < 60s>

## 同步链路
| 环节 | 组件 | 配置 | 说明 |
| --- | --- | --- | --- |
| 事件捕获 | <S3 Event / EventBridge> | <prefix: data/> | 新增/修改触发 |
| 传输执行 | <DTS / 自建 Worker> | <并发 20，限速 200 Mbps> | 断点续传 |
| 死信处理 | <DLQ> | <失败对象入队> | 单独重试 |
```

## 模板 2：同步任务配置

```yaml
source:
  endpoint: <s3-endpoint>
  bucket: <source-bucket>
  prefix: data/
  event: true
target:
  endpoint: oss-<region>.aliyuncs.com
  bucket: <target-bucket>
sync:
  full: once
  incremental: continuous
  delete_policy: mark
  retry:
    max_attempts: 3
    backoff: exponential
monitor:
  lag_threshold_s: 300
  backlog_threshold: 1000
```

## 模板 3：监控与告警

```markdown
| 指标 | 采集方式 | 告警阈值 | 级别 |
| --- | --- | --- | --- |
| 同步延迟 | <源 LastModified - 目标写入> | > 300s | P2 |
| 未同步积压 | <队列深度> | > 1000 | P2 |
| 失败率 | <失败/总对象> | > 0.01% | P1 |
```

## 模板 4：切流 Runbook

```markdown
| 步骤 | 操作 | 验证 | 回滚 |
| --- | --- | --- | --- |
| 1 读双跑 | <应用读两端，diff 告警> | <24h 差异 0> | - |
| 2 写双跑 | <新增双写> | <抽样一致> | <关双写> |
| 3 切读 | <100% 读目标> | <RT 一致> | <切回源> |
| 4 切写 | <停写源> | <业务验证> | <DTS 反向同步保留> |
```
