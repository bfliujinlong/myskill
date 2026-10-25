# GCP 免费层资源概览（2026年）

## Google Cloud 永久免费层

| 资源 | 免费额度 | 备注 |
|------|----------|------|
| Compute Engine | e2-micro (1vCPU, 1GB RAM) 每月 30GB 磁盘 | 美国地区 한정 |
| Cloud Storage | 5GB 标准存储 | - |
| Cloud Logging | 50GB/月 | - |
| Cloud Monitoring | 150MB 指标/月 | - |
| Cloud Functions | 2M 调用/月, 400,000 GB-秒 | - |
| Cloud Run | 2M 请求/月, 180,000 vCPU-秒, 360,000 GB-秒, 2GB 网络 | - |

## Google AI 免费层

### Gemini API (通过 Google AI Studio)

| 模型 | RPM | TPM | 每日请求上限 | 状态 |
|------|-----|-----|-------------|------|
| Gemini 2.0 Flash | 15 | 1M | ~1000 | ✅ 免费 |
| Gemini 2.5 Flash | 5-15 | 视情况 | ~1000 | ✅ 免费 |
| Gemini 3 Flash Preview | 10 | 250K | ~1500 | ✅ 免费 |
| Gemini 3.1 Flash-Lite Preview | 15 | 视情况 | ~1000 | ✅ 免费 |
| Gemini 2.5 Pro | 5 | - | 50 | ❌ 2026年4月起不再免费 |
| Gemini 3.1 Pro | - | - | - | ❌ 付费 |

> ⚠️ 速率限制是**按项目**计算的，不是按 API Key。

### Google Cloud $300 试用额度

新账户通常有 $300 试用额度，有效期 90天。适用于大多数付费服务。

## 注意事项

1. **GCP 永久免费层**与**试用额度**是分开的
2. 部分资源需要启用服务才计入免费额度
3. 免费 tier 资源在某些地区可能不可用
4. 监控费用：设置预算提醒，避免意外费用

## 配置建议

- 为项目设置**预算提醒**（50%、90%、100%）
- 启用**自动停止**资源的脚本（例如非工作时间停止 VM）
- 监控**网络出流量**（尤其是跨地域流量可能产生费用）