---
name: landing-zone-pm
description: "LZ项目管理：云 Landing Zone 规划、账号/网络/安全基线、交付里程碑与治理。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Landing Zone, LZ, 云底座, 账号治理, 安全基线, 项目管理]
    related_skills: [project-manager, cloud-migration, multi-cloud, presales-architect]
---

# LZ 项目管理（Landing Zone Project Management）

## When to Use（何时使用）

- 客户新建云环境，需要先搭「云底座/Landing Zone」再上业务
- 涉及多账号体系、统一网络、身份联邦、安全合规基线
- 需要把 LZ 交付拆成里程碑、做治理巡检
- 售前方案里 LZ 作为第一阶段的实施内容

## Landing Zone 六大支柱

1. **账号与组织（Organization）**
   - 多账号结构：管理账号 / 日志账号 / 安全账号 / 业务账号
   - 组织单元（OU）按环境（prod/dev）或业务线划分
   - 统一账单与配额管理

2. **身份与访问（IAM）**
   - 云原生账号 + 企业 IdP 联邦（SSO）
   - 最小权限、角色分离、特权账号审批
   - 密钥/凭据集中管理（KMS/密钥库）

3. **网络底座**
   - 共享 VPC / 中心辐射（Hub-Spoke）拓扑
   - 公网出口统一（NAT/防火墙）
   - 跨账号/跨地域互联（云企业网/专线）

4. **安全合规基线**
   - 必启安全服务：防护/审计/配置核查
   - 日志集中采集（操作日志+访问日志）
   - 等保/行业合规映射

5. **资源与成本治理**
   - 标签规范（env/owner/costcenter）
   - 预算告警（如 $0.1 阈值，见 multi-cloud / overseas-model-hub）
   - 资源配额与上限策略

6. **运维可观测**
   - 统一监控、告警通道（Telegram/短信/邮件）
   - 配置基线巡检（定期 drift 检测）

## 交付里程碑模板
| 阶段 | 交付物 | 验收 |
|------|--------|------|
| LZ 规划 | 架构图+账号规划 | 客户确认 |
| 基线搭建 | 账号/网络/IAM | 连通性+权限测试 |
| 安全加固 | 审计/防护/日志 | 合规扫描通过 |
| 治理上线 | 标签/预算/监控 | 告警可达 |
| 业务接入 | 首个业务落地 | 验收签字 |

## 常见陷阱
- 单账号一把梭，后期隔离/配额难拆
- 网络先随手建，业务一多就重构
- 安全服务没开，等保过不了
- 标签不规范，月底算不清谁花的钱
