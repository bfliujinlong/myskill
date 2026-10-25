---
name: cloud-pricing-tools
description: "查各云厂商价格，做对比和推荐。触发词：云价格/对比/报价。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloud-pricing, MCP, quotation, presales]
    related_skills: [presales-architect, spreadsheet-delivery]
---

# Cloud Pricing Tools

Multi-cloud pricing lookup via MCP servers and CLIs.

## MCP Availability (2026-09-02)

| Cloud | Package | Status |
|---|---|---|
| AWS | awslabs.aws-pricing-mcp-server | ✅ working |
| Azure | azure-mcp-server | ❌ no server entry |
| GCP | gcp-mcp | ❌ MCP v1→v2 incompatible |
| google-cloud | google-cloud-mcp | ❌ MCP v1→v2 incompatible |
| aliyun | none | ❌ |
| tencent | none | ❌ |
| huawei | none | ❌ |
| volcengine | none | ❌ |
| OCI | none | ❌ |

## AWS Pricing MCP Config

```yaml
mcp_servers:
  awslabs.aws-pricing-mcp-server:
    command: uvx
    args: [awslabs.aws-pricing-mcp-server@latest]
    env:
      FASTMCP_LOG_LEVEL: ERROR
    disabled: false
```

⚠️ **Do NOT set `AWS_PROFILE` or `AWS_REGION`** — the MCP fails with "config profile (default) could not be found" when `~/.aws/credentials` is absent. Without credentials, the server still serves public pricing data (On-Demand list prices). Only add `AWS_PROFILE` if the user has IAM credentials configured.

Call: `uvx awslabs.aws-pricing-mcp-server@latest --service AWSEC2 --region us-east-1`

## Batch Query Script

```python
import subprocess, json, os
services = ["AWSEC2","AWSRDS","AWSS3","AWSLambda","AWSEKS"]
results = {}
for svc in services:
    r = subprocess.run(
        ["uvx","awslabs.aws-pricing-mcp-server@latest","--service",svc,
         "--region","us-east-1"],
        capture_output=True,text=True,timeout=15
    )
    results[svc] = json.loads(r.stdout) if r.returncode==0 else {"error":r.stderr[:100]}
```

## Other Clouds — CLI fallback

- aliyun: `aliyun` CLI
- tencent: `tcloud` CLI
- huawei: `hcloud` CLI
- GCP: `gcloud` CLI
- Azure: `az` CLI

## Pitfalls

1. **hermes config set** treats dots as path separators — mangles `awslabs.aws-pricing-mcp-server` into nested dict. Fix YAML manually after set.
2. **uvx needs writable cache**: `mkdir -p /home/ubuntu/.cache/uv`
3. **MCP SDK v1→v2 breakage**: many cloud MCPs pinned to old `mcp.server.fastmcp` API.
