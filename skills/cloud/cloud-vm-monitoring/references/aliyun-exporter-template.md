# Aliyun OpenAPI Prometheus Exporter Template

Working pure-Python exporter that monitors Aliyun ECS/billing/disk via signed OpenAPI calls. No CLI or SDK dependency required.

## Architecture
- Single Python file (~300 lines), runs as systemd user service
- Listens on a configurable port (default `:9102`)
- Exposes `/metrics` (Prometheus format), `/health`, `/` (status page)
- 10-minute internal cache to avoid hitting API rate limits
- Scans multiple regions in one pass

## Signing Algorithm

```python
import hmac, hashlib, base64, urllib.parse, uuid
from datetime import datetime, timezone

def sign_request(params: dict, secret: str) -> str:
    sorted_params = sorted(params.items())
    query = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    string_to_sign = "GET&" + urllib.parse.quote("/", safe="") + "&" + urllib.parse.quote(query, safe="")
    h = hmac.new((secret + "&").encode(), string_to_sign.encode(), hashlib.sha1)
    return base64.b64encode(h.digest()).decode()

def call_api(endpoint, version, action, region="cn-shanghai", extra=None):
    params = {
        "Format": "JSON",
        "Version": version,
        "AccessKeyId": AK,
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Action": action,
        "RegionId": region,
    }
    if extra:
        params.update(extra)
    params["Signature"] = sign_request(params, SK)
    resp = httpx.get(f"https://{endpoint}/", params=params, timeout=15)
    return resp.json() if resp.status_code == 200 else {}
```

## Credential Loading

Reads AK/SK from `~/.aliyun/config.json` (same file used by aliyun CLI):

```python
def load_credentials():
    with open(os.path.expanduser("~/.aliyun/config.json")) as f:
        cfg = json.load(f)
    for p in cfg.get("profiles", []):
        if p.get("mode") == "AK":
            return p["access_key_id"], p["access_key_secret"]
    return cfg["profiles"][0]["access_key_id"], cfg["profiles"][0]["access_key_secret"]
```

## API Endpoints Used

| API | Endpoint | Version | Purpose |
|-----|----------|---------|---------|
| DescribeInstances | ecs.aliyuncs.com | 2014-05-26 | ECS inventory per region |
| DescribeDisks | ecs.aliyuncs.com | 2014-05-26 | Disk capacity |
| QueryAccountBill | business.aliyuncs.com | 2017-12-14 | Monthly billing |

## Metrics Exposed

```
alicloud_ecs_instances_total
alicloud_ecs_instances_running
alicloud_ecs_instances_stopped
alicloud_ecs_total_cpu
alicloud_ecs_total_memory_gb
alicloud_ecs_region_instances{region}
alicloud_ecs_instance_status{name,id,region,type,ip}
alicloud_ecs_instance_cpu{name,id,region,type,ip}
alicloud_ecs_instance_memory_gb{name,id,region,type,ip}
alicloud_billing_current_month{month}
alicloud_billing_previous_month{month}
alicloud_billing_product{product}
alicloud_disk_count
alicloud_disk_total_gb
```

## Prometheus Config Addition

```yaml
scrape_configs:
  - job_name: 'alicloud'
    scrape_interval: 300s
    static_configs:
      - targets: ['localhost:9102']
```

## Systemd User Service

```ini
[Unit]
Description=Alibaba Cloud Prometheus Exporter
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/ali-exporter
EnvironmentFile=%h/.env
ExecStart=/usr/bin/python3 %h/ali-exporter/aliyun_exporter.py
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

⚠️ Do NOT include `User=` or `Group=` in user-level services (causes 216/GROUP failure).
