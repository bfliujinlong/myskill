# 输出模板：对象存储迁移（OSS）

`<>` 为占位符，产出时替换。

## 模板 1：迁移方案书

```markdown
# 对象存储迁移方案

- 源端：<AWS S3 ap-southeast-1>，Bucket <N> 个，对象 <X> 亿，总量 <Y> TB
- 目标：<阿里云 OSS cn-hangzhou>，标准存储
- 迁移工具：<阿里云 OSS 在线迁移服务 / ossutil>
- 预计窗口：<2 周（限速 <M> Mbps）>

## Bucket 规划
| 源 Bucket | 目标 Bucket | 存储类型 | 生命周期规则 | 版本控制 |
| --- | --- | --- | --- | --- |
| <s3-prod-img> | <prod-img> | 标准 | <30 天转低频> | 开启 |
```

## 模板 2：迁移任务配置

```json
{
  "source": {
    "type": "aws_s3",
    "endpoint": "s3.ap-southeast-1.amazonaws.com",
    "bucket": "<source-bucket>",
    "prefix": "data/",
    "credential": "<iam_role_arn>"
  },
  "target": {
    "endpoint": "oss-cn-hangzhou.aliyuncs.com",
    "bucket": "<target-bucket>",
    "prefix": "data/"
  },
  "options": {
    "schedule": "02:00-06:00",
    "bandwidth_limit_mbps": 500,
    "multipart_size_mb": 50,
    "skip_existing": true
  }
}
```

## 模板 3：校验报告

```markdown
| Bucket | 对象数（源） | 对象数（目标） | 容量（源） | 容量（目标） | 抽样校验 | 结果 |
| --- | --- | --- | --- | --- | --- | --- |
| <prod-img> | <1.2 亿> | <1.2 亿> | <45 TB> | <45 TB> | <1000 CRC64> | ✅ |
```

## 模板 4：切流 Runbook

```markdown
## 切流步骤
| 步骤 | 操作 | 验证 | 回滚 |
| --- | --- | --- | --- |
| 1 | <修改应用 endpoint> | <新端点 4xx < 0.1%> | <切回源端> |
| 2 | <灰度 10%→100%> | <监控 30 min> | <保留源端 7 天> |
| 3 | <清理源端> | <客户书面确认> | <不可逆，需审批> |
```
