# GCP Usage Patterns & Session Learnings

## User's GCP Setup
- **Project**: `cryptic-bivouac-471612-t0`
- **VM**: `free-ubuntu-vm` in `us-central1-f`
- **Machine type**: `e2-micro` (free tier eligible)
- **Service account**: `237001753296-compute@developer.gserviceaccount.com`
- **Free trial**: $300 credit until 2026-11-15
- **Current billing**: $0.00 (fully offset by credits)

## Network Usage (as of 2026-08-17)
- Inbound: ~1.36 GB (free)
- Outbound: ~36 MB (well within 1 GB free tier)
- Cost: $0.00

## IAM Permission Gotcha
The VM's default service account lacks billing read permissions. Two ways to fix:

### Option 1: Add role via Cloud Shell (NO restart needed)
```bash
gcloud projects add-iam-policy-binding cryptic-bivouac-471612-t0 \
  --member="serviceAccount:237001753296-compute@developer.gserviceaccount.com" \
  --role="roles/billing.viewer"
```

### Option 2: Edit VM in Console (requires stop/start)
1. Stop VM
2. Edit → Service account → add Billing Account Viewer role
3. Start VM

⚠️ **CRITICAL**: Never stop the VM you are currently running on — you will lose connection and cannot restart it remotely. Use Cloud Shell instead.

## Mobile Cloud Shell Quirks
- Character limit truncates long commands
- Workaround: use shell variables for long arguments
- Example:
  ```bash
  SA=237001753296-compute@developer.gserviceaccount.com
  gcloud projects add-iam-policy-binding PROJECT_ID --member serviceAccount:$SA --role roles/billing.viewer
  ```

## Cron Job for Billing Monitoring
Created: "GCP 账单监控" (job_id: 2d995a116710)
- Schedule: daily at 08:00 UTC
- Delivers to: origin (Telegram)
- Note: Will fail until billing.viewer permission is granted to service account
