---
name: cloud-vm-deployment
description: "Deploy web apps on cloud VMs with Cloudflare DNS."
version: "1.0"
author: hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [cloud, deployment, docker, cloudflare, dns, aliyun, oci]
    related_skills: [oci-public-app-access, alibabacloud-opc-advisor]
---

# Cloud VM Deployment with Cloudflare DNS

## When to use
- Deploy a web app on a cloud VM (Aliyun ECS, OCI, etc.)
- Need to expose app via Cloudflare DNS (A record or tunnel)
- Docker containers with nginx need to coexist with host services
- SSH key-based access to cloud VM

## Step 1: SSH Access

```bash
ssh -i <key.pem> -o StrictHostKeyChecking=no root@<public-ip>
```

**Aliyun ECS**: Default user is `root`, key is `.pem` format.
**OCI**: Default user is `ubuntu` (ARM) or `opc` (x86), key can be `.pem` or `.key`.

## Step 2: Check Running Services

```bash
# Check Docker containers
docker ps --format '{{.Names}}\t{{.Status}}'

# Check port conflicts
ss -tlnp | grep -E ':80|:443|:8000|:3000'

# Check host nginx
systemctl status nginx 2>/dev/null
```

## Step 3: Resolve Port Conflicts

**Problem**: Host nginx and Docker container both want port 80.

**Solution A**: Stop host nginx, let Docker own port 80:
```bash
systemctl stop nginx
docker run -d --name <app> --restart=always -p 80:80 <image>
```

**Solution B**: Use Docker bridge network (recommended for multi-container apps):
```bash
# Create network
docker network create <app>_default

# Run containers on the network
docker run -d --name <app> --restart=always --network <app>_default -p 80:80 <image>
```

**Solution C**: Map container to different host port:
```bash
docker run -d --name <app> --restart=always -p 8080:80 <image>
# Then configure host nginx to proxy_pass to 127.0.0.1:8080
```

## Step 4: Configure Cloudflare DNS

### Option A: A Record (DNS only, gray cloud)

1. Login to https://dash.cloudflare.com
2. Select domain → DNS → Add record:
   - Type: A
   - Name: `<subdomain>` (e.g., `aicc`)
   - IPv4: `<public-ip>`
   - TTL: Auto
   - Proxy: OFF (gray cloud)

2. Verify: `dig <subdomain>.<domain> +short`

### Option B: Cloudflare Tunnel (more secure, no port opening)

```bash
# Install cloudflared
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o /tmp/cf.deb
dpkg -i /tmp/cf.deb

# Run with token
cloudflared tunnel run --token <cfut_token>
```

### Option C: API (requires DNS:Edit permission)

```python
import requests

CF_API_TOKEN = '<cfut_token>'
ZONE_ID = '<zone_id>'

headers = {
    'Authorization': f'Bearer {CF_API_TOKEN}',
    'Content-Type': 'application/json'
}

# Create A record
requests.post(
    f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records',
    headers=headers,
    json={
        'type': 'A',
        'name': '<subdomain>',
        'content': '<public-ip>',
        'ttl': 600,
        'proxied': False
    }
)
```

## Step 5: Verify

```bash
# Local check
curl -sI http://127.0.0.1:80 | head -5

# External check (after DNS propagates)
curl -sI http://<subdomain>.<domain> | head -5
```

## Pitfall: Cloudflare API Token Permissions

API Tokens with only `#zone:read` cannot create DNS records. You need:
- `Zone → DNS → Edit`
- `Zone → Zone → Read`

**Error**: `Authentication error` (code 10000) when creating records.
**Fix**: Generate new token at https://dash.cloudflare.com/profile/api-tokens with DNS:Edit permission.

## Pitfall: Cloudflare Global Key Auth

Global Key (`cfk_` prefix) requires exact email match:
```
X-Auth-Key: <global_key>
X-Auth-Email: <exact_account_email>
```

**Error**: `Authentication failed` (code 9106) when email doesn't match.
**Fix**: Use the exact email shown in Cloudflare dashboard → My Profile.

## Pitfall: Cloudflare API Credentials — 4-Level Auth Hierarchy

Cloudflare has 4 credential types. Using the wrong one gives a different error code:

| Credential | Format | Typical Error | Fix |
|------------|--------|---------------|-----|
| API Token (`cfut_`) | `Authorization: Bearer` | `10000 Authentication error` (missing permissions) | Need `DNS:Edit` + `Zone:Read` permissions |
| Global Key (`cfk_`) | `X-Auth-Key` + `X-Auth-Email` | `9106 Authentication failed` (email mismatch) | Use exact email from Cloudflare dashboard |
| Both together | Mixed headers | `9106 or 10000` | Pick one, don't mix |
| Session cookie | Browser-only | N/A | Use headless browser to login, extract cookie |

**Rule**: When API auth fails with `9106`, the email is wrong. When it fails with `10000`, the token lacks permissions. Check the error code first.

## Pitfall: Docker Host Network Breaks Inter-Container DNS

Using `--network host` makes containers lose Docker DNS resolution:
```
# BAD: host network breaks service discovery
docker run --network host <image>  # Can't resolve 'backend' hostname

# GOOD: bridge network preserves Docker DNS
docker run --network <app>_default <image>  # Can resolve 'backend'
```

**Rule**: Use bridge networks for multi-container apps that reference each other by service name.

## Pitfall: Overseas Email Registration Blocked

From German/EU IPs, most free email providers block registration:
- AOL: requires phone verification
- GMX: blocks German IPs entirely
- ProtonMail/Zoho: CAPTCHA required
- Yandex: requires phone verification
- Outlook: custom birthdate components resist automation

**Workaround**: Use existing email (Gmail, Outlook, etc.) or register from a non-EU IP.

## Pitfall: Docker Container with Internal Nginx

Some Docker images (e.g., `aicc-frontend`) run their own nginx inside the container. The container's nginx config may reference upstream services by Docker network name (e.g., `proxy_pass http://backend:8000`). This is the default for many frontend containers (React SPA + nginx reverse proxy).

**Symptom**: Container enters restart loop with error `host not found in upstream "backend"` or `emerg] host not found in upstream`.

**Resolution**: Run container on the same Docker bridge network as backend services:
```bash
docker stop <frontend>
docker rm <frontend>
docker run -d --name <frontend> --restart=always --network <app>_default -p 80:80 <image>
```

**What NOT to do**: `--network host` — this disables Docker DNS, so the container cannot resolve `backend` → `backend:8000`. The container will crash on startup with `host not found in upstream`.

**How to debug**: `docker logs <container> 2>&1 | grep -i error | tail -5` — look for `emerg] host not found in upstream`. Fix is to switch from host to bridge network.

## User Preference: Document Output Format (MD → DOCX)

When user asks for 报价/方案/交付物 in Word format, or says "输出word":

**Structure rules:**
- Each major section (## level heading) starts on a new page — insert page breaks via `docx.oxml`:
  ```python
  from docx.oxml import OxmlElement
  from docx.oxml.ns import qn
  def add_page_break(paragraph):
      run = paragraph.add_run()
      br = OxmlElement('w:br')
      br.set(qn('w:type'), 'page')
      run._r.append(br)
  ```
- Code blocks → **Consolas 8pt**, subtle gray color (RGB 50,50,50), capped at ~120 lines
- Heading hierarchy: # doc title, ## chapters, ### sub-sections
- Font: Microsoft YaHei for Chinese documents
- Clean HTML tags before conversion: remove `<details>/<summary>` → Markdown bold, `~~~text` → ` ```text `

**User preference**: default to .docx (not .md) unless .md is explicitly requested. Chapter-structured with page breaks.

## Multi-Tenant Platform Quotation (AC-MIG Standard)

For Alibaba Cloud multi-tenant platform quotations, follow this 8-section structure:

1. **Project Background** — region, deployment model, tenant tiers
2. **Scope & Assumptions** — in-scope, out-of-scope, assumptions (cloud account access, instance tiers, subscription basis)
3. **Resource Evaluation** — per-tier ECS/RDS/Tair specs, AI inference options, shared services (LZ, ACR, OSS, SLS, ALB)
4. **WBS** — phase breakdown: LZ Build → Per-Tenant Build → AI Layer → Data Migration → DR Test → PM & Handover
5. **Man-Day Estimation** — table format: `Role | Work Content | Days | Rate ($350) | Amount`. Separate per-tenant costs (e.g., `$1,225/tenant`) from fixed costs (e.g., `$5,600 LZ`).
6. **Commercial Summary** — professional services (fixed) + cloud resources (monthly estimate) + AI inference cost + payment terms (50/30/20) + validity (30 days)
7. **Outstanding Items** — numbered list of items requiring client confirmation before final pricing
8. **Terms & Conditions** — scope limitation, resource cost disclaimer, methodology reference, client responsibilities

**Output format**: English + Chinese versions as separate files (`Quotation_*.docx` / `报价_*.docx`). English version follows English business conventions, not literal translation.

**Per-tier cost breakdown** (example for 3-tier model):

| Component | Small | Medium | Large |
|-----------|-------|--------|-------|
| ECS (g9i) | 2×g9i.large | 2×g9i.xlarge | 3×g9i.2xlarge |
| RDS PostgreSQL 16 HA | 200 GB ESSD PL1 | 200 GB ESSD PL1 | 300 GB ESSD PL1 |
| Tair Redis | 1 GB | 2 GB | 4 GB |

Reference: `references/quotation-template.md`
