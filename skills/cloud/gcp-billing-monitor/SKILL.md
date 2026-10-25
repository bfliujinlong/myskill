---
name: gcp-billing-monitor
version: 1.0.0
category: cloud
description: Monitor GCP billing via cron, gcloud, and IAM alerts.
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [GCP, billing, cron, cost-monitor, cloud]
    related_skills: [cloud-vm-monitoring]
---

# GCP Billing Monitor

Use when a GCP project needs automated daily cost checks, billing alerts, or a cron-driven "gcloud billing" summary delivered to a chat channel.

## When to Use

- You want a daily summary of GCP project billing/spend delivered to a chat (Telegram, WeChat, etc.).
- You're setting up cost monitoring for a GCP project and need the IAM + cron pieces wired up.
- You want to detect unexpected spend early and alert on thresholds.

## What This Covers

1. Granting the VM/service-account the right IAM role to read billing data.
2. Setting up a daily cron job that runs `gcloud billing` commands and delivers a summary.
3. Common pitfalls that block the above (scopes, account pinning, role placement).

## IAM: Where to Grant the Role

**Grant at the billing account level, NOT the project level.**

The role `roles/billing.viewer` is a *billing account* role. Attempting to bind it with `gcloud projects add-iam-policy-binding` will fail with:

```
Role roles/billing.viewer is not supported for this resource.
```

Correct command shape:

```bash
# 1. Find the billing account id for the project
gcloud billing projects describe PROJECT_ID
# reads: billingAccountName: billingAccounts/0137DE-0D1BAB-37E0B4

# 2. Grant at the billing account level
gcloud billing accounts add-iam-policy-binding BILLING_ACCOUNT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/billing.viewer"
```

## Pitfalls

### 1. Cloud Shell auth pins to the VM service account

Even after `gcloud auth login` succeeds in Cloud Shell, the *active account* (`core/account`) may remain the VM's compute service account (`*-compute@developer.gserviceaccount.com`). IAM writes (like `add-iam-policy-binding`) will fail with:

```
Request had insufficient authentication scopes.
... ACCESS_TOKEN_SCOPE_INSUFFICIENT
```

Diagnosis:

```bash
gcloud auth list          # look at the ACTIVE column
gcloud config get-value account
```

Fix: switch active account to a user account that has Owner/Billing Admin on the billing account:

```bash
gcloud config set account USER_EMAIL
```

Then retry the billing-account IAM command. If the user credential isn't present, `gcloud auth login` (with browser) is the most reliable path in Cloud Shell; `--no-browser` flows often don't complete inside a non-interactive or headless context.

### 2. `gcloud billing projects describe` argument

`gcloud billing projects describe PROJECT_ID` does **not** accept `--billing-account`. If you pass it, you get:

```
unrecognized arguments: --billing-account=...
```

The command infers billing from the project. If you need to reference a specific billing account for other commands, use `gcloud billing accounts ...` subcommands.

### 3. Role too broad vs. too narrow

- `roles/billing.viewer` — read-only billing data; enough for cost checks.
- `roles/billing.admin` — full billing admin; more than needed for monitoring.
- `roles/project.billing.manager` (Project Billing Manager) — project-level billing management, a different scope; visible in project IAM but does **not** replace the billing-account-level role for reading billing account data.

For a cost-monitoring use case, `roles/billing.viewer` at the billing-account level is the intended minimum.

## Cron Job Setup

### Create the daily check job

The job should run `gcloud billing` commands and deliver a summary to the user's chat.

```bash
# Example: daily at 09:00 UTC (adjust timezone to user's preference)
hermes cronjob create \
  --name "GCP 账单监控" \
  --schedule "0 9 * * *" \
  --prompt "检查 GCP 项目 ACCOUNT 的账单状态：\n1. 运行 gcloud billing projects describe ACCOUNT\n2. 运行 gcloud billing accounts list\n3. 汇总当日/累计费用信息，按资源（VM、流量等）列明细\n4. 若发现异常（如意外流量激增）给出明确警报\n5. 用简洁中文回复，包含关键数字和资源明细"
```

### Delivery target

Delivered back to the user's chat by default (`deliver: origin`). For multi-channel fan-out, set `deliver` explicitly.

### Verifying the job is wired

```bash
hermes cronjob list
# confirm the job shows schedule 0 9 * * * and state scheduled
```

### Manual run for testing

```bash
hermes cronjob run --job-id <job_id>
# or for a one-shot test, run the gcloud commands directly:
gcloud billing projects describe PROJECT_ID
gcloud billing accounts list
```

### 4. SERVICE_DISABLED on cloudbilling.googleapis.com cannot be self-healed from a low-privilege SA

`gcloud billing accounts list` / `projects describe` / REST `billingAccounts` may return 403 with
`Cloud Billing API has not been used in project <numeric-id> before or it is disabled` (reason SERVICE_DISABLED).
Enabling it needs `serviceusage.services.enable`; a minimal service account gets
`PERMISSION_DENIED: Permission denied to enable service [cloudbilling.googleapis.com]` — the API stays
disabled and no cost figure is obtainable. Enabling is a **console action by a user with Owner/Billing Admin**
at the activation URL, or `gcloud services enable` from an Owner account. Do not report "cost = $0" in this
state: it means "unknown", not "free".

### 5. Current blocked state on this host (verified 2026-10-24)

On the Hermes host (project `cryptic-bivouac-471612-t0`, numeric 237001753296):

- Active account = `mygemini@…-t0.iam.gserviceaccount.com`. `gcloud billing accounts list`,
  `projects describe`, even `projects list` all fail with **SERVICE_DISABLED** on
  `cloudbilling.googleapis.com` / `cloudresourcemanager.googleapis.com`.
- `gcloud services enable cloudbilling.googleapis.com` fails:
  `PERMISSION_DENIED … serviceusage.services.enable` (AUTH_PERMISSION_DENIED). The SA cannot self-heal.
- The compute SA `237001753296-compute@developer.gserviceaccount.com` gets
  `ACCESS_TOKEN_SCOPE_INSUFFICIENT` on `compute instances list`.

=> On this host the cost figure is **unknown**, never "$0". Report it as UNKNOWN and say the console
activation URL must be opened by an Owner/Billing Admin.

### 6. SMS channel is not configured — do not claim it sent

`gcp-billing-monitor.py` reads `SMS_GATEWAY_URL` / `TWILIO_*`; neither exists in `~/.hermes/.env`.
`send_sms()` returns `(False, "未配置")` — that is the honest result; never report SMS as delivered.
Only Telegram is a real configured channel (`hermes send --list` → `telegram:jinlongliu`).

### 7. Inside a cron run, the script's own Telegram send is a no-op

When the monitor runs from a cron job whose deliver target is the same Telegram chat, `hermes send`
prints: "Skipped send_message … this cron job will already auto-deliver its final response".
The script still exits 0. So: put the real report in the cron's final response; the in-script send
is only meaningful for manual/interactive runs.

### 8. (renumbered) The VM's default compute SA has insufficient scopes

`*-compute@developer.gserviceaccount.com` typically yields `ACCESS_TOKEN_SCOPE_INSUFFICIENT` for billing
and compute list calls even for its own project; switching accounts does not fix it while the VM was created
with narrow access scopes. Only a user account (or a SA key with the right roles) works.

## Existing Jobs to Reuse / Migrate

If a GCP billing check job already exists (e.g. created earlier with a different schedule), update it rather than creating a duplicate:

```bash
hermes cronjob list               # find the job id
hermes cronjob update --job-id <id> --schedule "0 9 * * *"
```

## References

- `references/gcp-billing-iam-and-cron.md` — command sequence, role matrix, IAM pitfall detail, and a condensed troubleshooting checklist.