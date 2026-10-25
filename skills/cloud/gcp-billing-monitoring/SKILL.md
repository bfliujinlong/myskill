---
name: gcp-billing-monitoring
category: cloud
description: 配置 GCP 账单监控、IAM 权限和每日检查告警
version: 1.0.0
author: auto-generated
license: MIT
metadata:
  hermes:
    tags: [GCP, billing, monitoring, cron, IAM]
    homepage: https://github.com/NousResearch/hermes-agent
---

# GCP Billing Monitoring

## 触发条件

- 用户需要监控 GCP 项目的费用/账单
- 需要配置 IAM 权限让服务账号可读取账单
- 需要设置每日/定期账单检查任务
- 需要配置预算告警

## 核心知识

### 1. IAM 权限层级

**关键区别：项目级 vs 账单账户级**

```
❌ 错误做法：在项目 IAM 中添加 Billing Viewer
  → roles/billing.viewer 对项目资源不适用

✅ 正确做法：在账单账户级别添加权限
  gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/billing.viewer"
```

### 2. 获取账单账户 ID

```bash
gcloud billing projects describe PROJECT_ID
# 输出示例：
# billingAccountName: billingAccounts/0137DE-0D1BAB-37E0B4
```

提取 `0137DE-0D1BAB-37E0B4` 即为账单账户 ID。

### 3. 验证权限是否生效

```bash
gcloud billing accounts get-iam-policy BILLING_ACCOUNT_ID
# 应包含刚添加的 binding

gcloud billing projects describe PROJECT_ID
# 应能正常返回账单信息
```

### 4. 网络/认证注意事项

- **Cloud Shell 中：** 如果当前认证的是 VM 服务账号（`compute@developer.gserviceaccount.com`），需要先切换到有权限的个人账号
  ```bash
  gcloud auth login  # 用浏览器登录个人账号
  gcloud config set account bfyalong@gmail.com
  ```

- **从网页端 Cloud Shell：** 如果从 GCP Console 网页打开 Cloud Shell，通常会用浏览器里的 Google 账号认证，具有更高权限

### 5. 配置每日检查 cron

在 Hermes 中创建每日账单检查任务：

```bash
# 使用 cronjob 工具创建
cronjob create \
  --name "GCP 账单监控" \
  --schedule "0 9 * * *" \
  --prompt "检查 GCP 项目 cryptic-bivouac-471612-t0 的账单状态..."
```

或者在 config.yaml 中配置后使用 hermes config set。

## 常见问题

### Q: 为什么在项目 IAM 中找不到 Billing Viewer 角色？

A: 因为 `roles/billing.viewer` 是**账单账户级别**的角色，不是项目级别的。需要去账单账户的 IAM 页面设置。

### Q: 命令返回 "insufficient authentication scopes"？

A: 当前认证的身份（通常是 VM 服务账号）没有权限修改 IAM 策略。需要：
1. 在 Cloud Shell 中用个人账号重新认证
2. 或在 GCP Console 网页上手动添加权限

### Q: 创建了 API Key 但是调用返回 401？

A: Google 正在从 Standard API Key 迁移到 Auth API Key。2026年9月起 Standard Key 将被拒绝。需要创建新的 Auth 类型 Key。

## 参考

- [GCP 免费资源](references/gcp-free-tier.md)
- [Google Gemini API 密钥迁移](references/gemini-api-key-migration.md)