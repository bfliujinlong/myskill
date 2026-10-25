# Cross-Cloud Pricing Comparison Workflow

## Use Case
Customer asks for AWS vs Alibaba Cloud (or other cloud) price comparison for a quotation or migration proposal.

## Data Sources

### AWS (via MCP — works without credentials)
```yaml
mcp_servers:
  awslabs.aws-pricing-mcp-server:
    command: uvx
    args: [awslabs.aws-pricing-mcp-server@latest]
    env:
      FASTMCP_LOG_LEVEL: ERROR
```
- Works without `~/.aws/credentials` for public On-Demand pricing
- China regions (Beijing, Ningxia): use `www.amazonaws.cn/en/ec2/pricing/` when MCP fails

### Alibaba Cloud (no MCP available)
- Scrape `https://www.aliyun.com/price/product` or `https://developer.aliyun.com/article/1717196`
- No public pricing API without AK/SK
- Use `aliyun` CLI if credentials configured

### Other Clouds
- GCP: `gcloud` CLI or `https://cloud.google.com/compute/vm-instance-pricing`
- Azure: `az` CLI or `https://azure.microsoft.com/en-us/pricing/details/virtual-machines/`
- Tencent: `tcloud` CLI

## Comparison Output Format

### Markdown Table (for quick reference)
| Spec | Cloud A | Cloud B | Savings |
|------|---------|---------|---------|
| 2v8G | ¥392.8/mo | ¥290.5/mo | 26% |

### Excel Quotation (for customer delivery)
Use `spreadsheet-delivery` skill with Anchanet Fintech template:
1. Copy `Express_Logistics_Quotation_LZ_Migration_V1.xlsx`
2. Modify Landing Zone sheet for Cloud A
3. Modify Migration sheet for Cloud B
4. Add comparison columns (Cloud A price, Cloud B price, Savings %)
5. LibreOffice recalc before sending

## Key Pricing Notes (2026-09)

### AWS China (Ningxia)
- m8g.large (2v8G ARM): ¥0.5381/hr = ¥392.8/mo
- m8g.xlarge (4v16G ARM): ¥1.0762/hr = ¥785.6/mo
- t4g.large (2v8G ARM): ¥0.2957/hr = ¥215.9/mo
- Data transfer out: ¥0.6003/GB (inter-region), ¥0.12/GB (to internet, first 10TB)
- EBS gp3: ¥0.55/GB/mo

### Alibaba Cloud (Hangzhou)
- ecs.g8i.large (2v8G Xeon): ¥0.398/hr = ¥290.5/mo
- ecs.g8i.xlarge (4v16G Xeon): ¥0.796/hr = ¥581.1/mo
- ecs.e-c1m1.large (2v8G): ¥0.18/hr = ¥131.4/mo (economy)
- Data transfer out: ¥0.8/GB (more expensive than AWS)
- ESSD PL1: ¥0.664/GB/mo (slightly more expensive than AWS gp3)

### Cost Optimization Tips
- AWS Spot/Up to 90% off vs Alibaba Cloud spot/Up to 70% off
- AWS RI savings: up to 74% vs Alibaba Cloud: up to 70%
- Alibaba Cloud data transfer is more expensive — factor this into TCO
- For migration proposals: Alibaba Cloud ~30-55% cheaper on compute, but factor in data transfer costs

## Pitfalls
1. **AWS MCP without credentials**: Works for public pricing, fails for account-specific billing
2. **Alibaba Cloud no MCP**: Must scrape or use CLI with AK/SK
3. **Currency**: AWS China prices in CNY, Alibaba Cloud in CNY — direct comparison valid
4. **Region mismatch**: Always compare same-tier regions (e.g., AWS Ningxia vs Alibaba Hangzhou, both tier-1)
5. **Data transfer**: Often overlooked — can negate compute savings for data-heavy workloads
