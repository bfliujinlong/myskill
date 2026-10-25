# GCP Billing IAM + Cron Reference

Condensed command sequence and pitfalls for wiring GCP billing read access + a daily cron check.

---

## GCP 小额收费避坑（实测 2026-08）

- 本月账单 ≈ $0.15，其中 **Compute Engine = $0.00**（VM 在免费层，没花钱）。
- 主要收费源是**网络分析类功能**：
  - **Network Topology**（网络拓扑可视化）：~$0.05/月，控制台打开过就会持续监控 VPC 拓扑并按小时计费。
  - **Network Analyzer**（基于 VPC Flow Logs 的分析）：~$0.05/月。
- **结论**：不去开网络拓扑图 / 不跑网络分析，这两项 $0.10 就没有，月账单可归零。
- 免费层 VM 始终 $0，无需担心；设的 $0.1 告警阈值已覆盖异常情况。
- 关闭方式：控制台 VPC Network → Network Topology 关闭监控；或避免再次打开相关页面。

---

## 1. Find the billing account for a project

```bash
gcloud billing projects describe PROJECT_ID
```

Typical output:

```
billingAccountName: billingAccounts/0137DE-0D1BAB-37E0B4
billingEnabled: true
name: projects/PROJECT_ID/billingInfo
projectId: PROJECT_ID
```

The billing account ID is the segment after `billingAccounts/`, e.g. `0137DE-0D1BAB-37E0B4`.

## 2. Grant billing read access

Grant at the **billing account** level, not the project level.

```bash
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/billing.viewer"
```

**Do not use** `gcloud projects add-iam-policy-binding` for `roles/billing.viewer` — it will reject the role as unsupported for the resource.

## 3. Verify the grant

### Check billing account IAM policy

```bash
gcloud billing accounts get-iam-policy BILLING_ACCOUNT_ID
```

Look for a binding with `member: serviceAccount:SERVICE_ACCOUNT_EMAIL` and the intended role.

### Check project IAM (for context)

```bash
gcloud projects get-iam-policy PROJECT_ID
```

This shows project-level roles (e.g. Project Billing Manager) but does **not** replace the billing-account-level grant for reading billing data.

## 4. Role matrix (what each role means here)

| Role | Scope | What it lets you do | Suitable for cost monitoring? |
|------|-------|---------------------|-------------------------------|
| `roles/billing.viewer` | Billing account | Read billing account & project billing info | ✅ Yes — intended minimum |
| `roles/billing.admin` | Billing account | Full billing admin (manage payment, etc.) | ⚠️ Over-broad for read-only |
| `roles/project.billing.manager` (Project Billing Manager) | Project | Project-level billing management | ❌ Not a substitute for billing-account read access |

## 5. Common failure: Cloud Shell auth pins to VM service account

Even after a successful `gcloud auth login`, Cloud Shell may keep the **active account** as the VM's compute service account:

```
ACTIVE  ACCOUNT
*       237001753296-compute@developer.gserviceaccount.com
```

That account often lacks the permission to call `getIamPolicy` on the billing account, producing:

```
Request had insufficient authentication scopes.
... ACCESS_TOKEN_SCOPE_INSUFFICIENT
... method: google.cloud.billing.v1.CloudBilling.GetIamPolicy
```

### Diagnose

```bash
gcloud auth list
gcloud config get-value account
```

### Fix

```bash
gcloud config set account USER_EMAIL   # the account with Owner/Billing Admin on the billing account
```

Then retry the billing-account IAM command. If the user credential isn't present in Cloud Shell, `gcloud auth login` with a browser flow is usually the most reliable path; `--no-browser` remote flows can stall in non-interactive sessions.

## 6. Daily cron job (Hermes)

### Create

```bash
hermes cronjob create \
  --name "GCP 账单监控" \
  --schedule "0 9 * * *" \
  --prompt "检查 GCP 项目 PROJECT_ID 的账单状态：\n1. 运行 gcloud billing projects describe PROJECT_ID\n2. 运行 gcloud billing accounts list\n3. 汇总费用信息，按资源列明细\n4. 异常时给出明确警报\n5. 用简洁中文回复"
```

### Migrate an existing job (don't duplicate)

```bash
hermes cronjob list                     # find job id
hermes cronjob update --job-id <id> --schedule "0 9 * * *"
```

### Manual test run

```bash
gcloud billing projects describe PROJECT_ID
gcloud billing accounts list
```

## 7. Notes

- `gcloud billing projects describe` does **not** accept `--billing-account`. It infers billing from the project.
- After IAM changes, allow a few minutes for the policy to propagate before testing.
- For multi-channel notification, set the cron's `deliver` field rather than relying on default origin-only delivery.
