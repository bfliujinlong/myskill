---
name: aws-pricing-anon
description: 匿名获取 AWS 官方定价（无需 AK/SK、无需登录、零费用）。用于迁移评估/报价/TCO 对比时取 AWS On-Demand 真实单价。触发词：AWS 价格、AWS 报价、AWS TCO、EC2 单价、AWS 定价对比、迁移成本估算。
---

# AWS 匿名定价查询（零凭据）

## 为什么存在
AWS Price List API (`pricing.amazonaws.com`) **必须**要有 AK/SK，本环境无 AWS 凭据。
但 AWS 公开的 **Pricing Calculator 数据源** (`b0.p.awsstatic.com`) 与 **Bulk API** (`pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json`)
是**完全匿名、免费、无需任何凭据**的，且为 AWS 官方发布数据。本 skill 走这条路径。

## 安全边界
- 只读、匿名、零费用。不发送任何密钥，不做任何写操作。
- 仅取 On-Demand 公开单价，不含客户折扣/RI/SP。报价必须标注「公开价」。

## 用法

### 取 EC2 On-Demand（推荐，文件小 ~700KB）
```bash
python3 /home/ubuntu/.hermes/skills/aws-pricing-anon/aws_price.py ec2 --region "US East (N. Virginia)" --os Linux --match t3.micro
```

### 列出可用 region / 服务
```bash
python3 /home/ubuntu/.hermes/skills/aws-pricing-anon/aws_price.py regions
python3 /home/ubuntu/.hermes/skills/aws-pricing-anon/aws_price.py services
```

## 数据源
- 主：`https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/<Region>/<OS>/index.json`
  - 必须带 `--compressed`（服务端 gzip）
- 备：`https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json`（匿名，Bulk API 索引，EC2 全量索引 481MB 慎用）

## 已验证事实（2026-10-31 实测）
- Bulk index.json 匿名可下载，publicationDate 2026-10-30
- EC2 全量 region 索引 481,649,899 B（太重，勿用）
- Pricing Calculator 端点 695,489 B（gzip），含 vCPU/Memory/price 字段
- t3.small us-east-1 Linux = **$0.0208/hr**（实测）

## 报价注意
公开价 ≠ 成交价。写入报价单时必须注明「AWS 公开 On-Demand 单价，未含 RI/SP/EDP 折扣」。
