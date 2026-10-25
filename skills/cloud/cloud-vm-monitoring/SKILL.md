---
name: cloud-vm-monitoring
description: "Monitor cloud VM costs and network usage."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloud, gcp, vm, billing, monitoring, free-tier, mobile]
---

# Cloud VM Cost & Usage Monitoring

Monitor cloud VM instances for cost overruns, especially free-tier instances. Focused on GCP with broadly applicable patterns.

## When to use
- User runs a cloud VM (especially free tier) and worries about billing
- User wants to monitor network traffic, disk, or compute usage
- User needs to set up cost alerts or billing checks
- User is managing cloud resources from a mobile device

## GCP Free Tier Reference
| Resource | Free Limit | Notes |
|----------|-----------|-------|
| e2-micro VM | 1 instance/month | us-central1 region only |
| Standard disk | 30 GB/month | |
| Outbound traffic | 1 GB/month | From North America, excludes China/Australia |
| Inbound traffic | Unlimited | Always free |

## Checking Network Usage (from inside VM)
```bash
cat /proc/net/dev
```
Look at the primary network interface (e.g., `ens4`) for bytes received (inbound, free) and transmitted (outbound, counts against free tier).

Example output interpretation:
```
ens4: 1457061931  261748  ...  36351821  125227
         ^recv bytes          ^transmit bytes
```
In this example: ~1.36 GB inbound (free), ~36 MB outbound (within 1 GB free tier).

## IAM Management Without Downtime
You can modify IAM permissions WITHOUT stopping the running VM:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/billing.viewer"
```
Permissions take effect immediately. No restart needed.

⚠️ **PITFALL**: Do NOT stop the VM you are running on — you will lose connection and cannot restart it remotely. Use Cloud Shell (in GCP Console or mobile app) to manage the VM instead.

## Mobile Cloud Shell Command Truncation
Mobile Cloud Shell has a character limit that can truncate long commands. Workaround with variables:
```bash
SA=very-long-service-account@project.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding my-project --member serviceAccount:$SA --role roles/billing.viewer
```

## VM Metadata (from inside the VM)
```bash
curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google"
curl -s "http://metadata.google.internal/computeMetadata/v1/instance/name" -H "Metadata-Flavor: Google"
curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google"
curl -s "http://metadata.google.internal/computeMetadata/v1/instance/machine-type" -H "Metadata-Flavor: Google"
```

## Aliyun ECS Monitoring via Prometheus

When monitoring Aliyun ECS instances from an external host (e.g., OCI jump box):
1. Write a pure-Python Prometheus exporter using `httpx` + manual HMAC-SHA1 signing of OpenAPI calls — avoids CLI/SDK dependency problems on ARM or in containers where `pip install` times out or architecture mismatches cause segfaults.
2. Sign each request with `AccessKeyId`, `SignatureMethod=HMAC-SHA1`, `Timestamp`, `SignatureVersion=1.0`, `SignatureNonce` (UUID), `Format=JSON`, `Version=2014-05-26`. Build the canonical query string sorted by key, URL-encode each param, join with `&`, then `HMAC-SHA1(key="<secret>&", text="GET&%2F&" + urlencode(query_string))` base64-encoded.
3. Query: `DescribeInstances` (per region), `QueryAccountBill` (monthly billing), `DescribeDisks` (storage).
4. Expose metrics on a local port (e.g., `:9102`), add as a Prometheus scrape target with generous interval (300s is fine for billing data).
5. Import a Grafana dashboard JSON via `POST /api/dashboards/db` with auth header.

See `references/aliyun-exporter-template.md` for the working exporter code.

### Pitfalls
- **Do NOT copy a CLI binary into a container of different architecture** — an x86_64 binary segfaults instantly on aarch64 (exit 139). Write pure Python instead.
- **Do NOT `pip install` vendor SDKs inside Docker containers** — network timeouts are common and the signing logic is straightforward enough to inline (~30 lines).
- **Cloud Assistant as backdoor** — when SSH to an Aliyun ECS fails (wrong key pair, security group blocks), use `aliyun ecs RunCommand` to inject your public key into `authorized_keys`. Works even when the instance is unreachable from outside.
- **Aliyun CLI profiles** — the CLI uses `~/.aliyun/config.json` with named profiles. Copy this file to the target (container/remote host) to provide AK/SK without exposing them in code.

## Grafana Dashboard via API

Import dashboards programmatically without UI:
```bash
curl -X POST http://127.0.0.1:3001/api/dashboards/db \
  -u "admin:<password>" \
  -H "Content-Type: application/json" \
  -d @dashboard.json
```
The JSON body wraps panels in `{"dashboard": {...}, "overwrite": true, "folderId": 0}`. Set `"id": null` and `"uid": "my-uid"` for a stable URL.

**Pitfall**: Grafana default `admin:admin` almost never works after any customization — check environment variables (`GF_SECURITY_ADMIN_PASSWORD`), custom ini, or provisioning files for the actual password before attempting API calls.

## Systemd User Services

When writing a user-level systemd service (`~/.config/systemd/user/*.service`):
- Do NOT include `User=` or `Group=` in `[Service]` — user services always run as the owning user. Specifying these causes a `216/GROUP` startup failure.
- Use `EnvironmentFile=%h/path/to/.env` to load secrets without hardcoding.
- After creating/editing: `systemctl --user daemon-reload && systemctl --user enable --now <name>.service`

## Cloudflare Tunnel — Remote-Managed Mode

When `cloudflared` runs with `--token <jwt>` (Zero Trust dashboard-managed), route/hostnames are managed remotely, NOT from a local `config.yml`. To add a hostname route:
1. Use CF API: `PUT /accounts/{id}/cfd_tunnel/{tunnel_id}` with updated `config.ingress` array — requires a valid API Token (not the tunnel run token).
2. Or log into the CF Zero Trust dashboard and add the Public Hostname manually.

**Pitfall**: The `cfut_` tunnel run token and the CF API Token are different credentials. The run token cannot add routes. If the API token expires or is revoked, routes can only be added via the web console.
