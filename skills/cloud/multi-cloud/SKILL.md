---
name: multi-cloud
description: "多云管理：跨云账号、统一网络、成本对账、厂商差异与容灾互备。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [多云, 跨云, 混合云, 成本对账, 容灾, multi-cloud]
    related_skills: [cloud-migration, landing-zone-pm, project-manager]
---

# 多云管理（Multi-Cloud Management）

## When to Use（何时使用）

- 客户同时使用 ≥2 家云（如阿里云+AWS、GCP+华为云）
- 需要统一身份、统一网络互联、跨云成本对账
- 做跨云容灾/互备、避免厂商锁定
- 评估各云性价比，做负载分布

## 核心模块

### 1. 统一身份
- 企业 IdP（如 Azure AD/Okta/钉钉）联邦到各云 SSO
- 一套账号体系，避免每云各建一套人肉账号
- 集中特权账号审批与审计

### 2. 跨云网络
- 互联方式：专线/VPN/云企业网（如阿里 CEN、AWS TGW、GCP NCC）
- 出网成本重点：跨云流量单价高，尽量同云内闭环
- 统一 DNS 与出口策略

### 3. 成本对账
每月拉各云账单，按 `costcenter/env/owner` 标签汇总：
| 云 | 计算 | 存储 | 网络出网 | 其他 | 合计 |
|----|------|------|----------|------|------|
| 阿里云 | | | | | |
| AWS | | | | | |
| GCP | | | | | |
> 重点盯「出网流量」和「跨区传输」，往往是隐性大头（参考 overseas-model-hub 里 GCP 流量监控）

### 4. 厂商差异速查
- 同名服务口径不同（如「负载均衡」各家计费模型不一）
- 区域命名不同，做映射表
- API/SDK 差异，用 Terraform 等 IaC 抹平

### 5. 容灾互备
- 双活 vs 冷备：按 RTO/RPO 选
- 数据跨云复制的合规与成本权衡
- 故障切换演练（别等真故障才发现切不过去）

## 常见陷阱
- 多云=多套账单+多套运维，没统一治理反而更贵
- 跨云流量费忽略，月底账单惊吓
- 容灾只配不演练，切换时全链路不通
- 厂商锁定没评估，关键时刻挪不动
