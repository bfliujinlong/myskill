# {{客户名}} {{项目名}} 高级架构设计（HLD）（AWS黑）

> 色系皮肤：`--brand aws`（渲染时由 `scripts/build_docx.py` 套用 AWS 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 密级：L2-内部级
> 目标云：**AWS** ｜ 状态：{{draft|final}}
> 输入事实源：`pcs-factsheet` 结构化 facts（目标云未定时先走 `pcs-arch-selection`）

---

## 0. 设计原则与总体架构

**0.1 设计原则**：{{≤6 条，每条一句话，禁止排比堆砌}}
**0.2 总体架构**：{{一段话叙述：源端 → 目标端的分区与关键路径}}
**0.3 领域覆盖一览**

| # | 领域 | 章节 | 设计结论（一句话） |
|---|---|---|---|
| 1 | 账号与组织架构 | 见 {{第1章}} | {{设计要点}} |
| 2 | 网络架构 | 见 {{第2章}} | {{设计要点}} |
| 3 | 安全与合规 | 见 {{第3章}} | {{设计要点}} |
| 4 | 身份与访问（IAM） | 见 {{第4章}} | {{设计要点}} |
| 5 | 计算 | 见 {{第5章}} | {{设计要点}} |
| 6 | 存储 | 见 {{第6章}} | {{设计要点}} |
| 7 | 数据库 | 见 {{第7章}} | {{设计要点}} |
| 8 | 监控与运维 | 见 {{第8章}} | {{设计要点}} |

> 8 大领域一一对应 `pcs-hld` 判据；任一领域留空即为未完成。

## 1. 账号与组织架构

**1.1 设计要点**：AWS Organizations + Control Tower；OU 结构（Security / Log Archive / Shared Services / Workloads）；SCP 护栏；Consolidated Billing 与成本分配标签

**1.2 关键组件**：{{按 AWS 官方服务名填写}}

**1.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**1.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 2. 网络架构

**2.1 设计要点**：VPC + Subnet（public / private / isolated 三层）；Transit Gateway 做多账号互联；Direct Connect + Site-to-Site VPN 冗余；ALB / NLB；NAT Gateway；Route 53

**2.2 关键组件**：{{按 AWS 官方服务名填写}}

**2.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**2.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 3. 安全与合规

**3.1 设计要点**：GuardDuty / Security Hub / Inspector；WAF + Shield；KMS；Config 规则；CloudTrail Organization Trail；IAM Access Analyzer；合规框架映射（由甲方确定适用项）

**3.2 关键组件**：{{按 AWS 官方服务名填写}}

**3.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**3.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 4. 身份与访问（IAM）

**4.1 设计要点**：IAM roles / users / policies；IAM Identity Center（SSO）；Permission Boundary；跨账号 Role 承担；SCP 约束

**4.2 关键组件**：{{按 AWS 官方服务名填写}}

**4.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**4.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 5. 计算

**5.1 设计要点**：EC2 实例族（m7i / c7i / r7i，以目标 Region 实际可用为准）；Auto Scaling Group；EKS；Launch Template + AMI

**5.2 关键组件**：{{按 AWS 官方服务名填写}}

**5.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**5.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 6. 存储

**6.1 设计要点**：S3（Standard / IA / Glacier）；EBS gp3 / io2；EFS；S3 Replication；Lifecycle 策略

**6.2 关键组件**：{{按 AWS 官方服务名填写}}

**6.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**6.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 7. 数据库

**7.1 设计要点**：RDS / Aurora；DynamoDB；ElastiCache；DMS（迁移 + CDC + 校验）；Redshift

**7.2 关键组件**：{{按 AWS 官方服务名填写}}

**7.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**7.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 8. 监控与运维

**8.1 设计要点**：CloudWatch（Metrics / Logs / Alarms）；CloudTrail；X-Ray；EventBridge 告警路由；SNS 通知

**8.2 关键组件**：{{按 AWS 官方服务名填写}}

**8.3 选型理由**：{{一句话：为什么是这个，而不是另一个}}

**8.4 待确认**：{{依赖甲方提供的信息，没有就写「无」}}

## 9. 高可用与容灾

**9.1 可用性目标**：{{SLA / RTO / RPO，未确认写「待确认」}}
**9.2 容灾策略**：{{同城多 AZ / 异地灾备，按 AWS 服务实现}}

## 10. 成本与优化

**10.1 资源清单与费用估算**：{{引用 mig-sizeng-advice / pcs-lz-estimate 输出}}
**10.2 优化建议**：{{预留实例 / 存储分层 / 闲置回收}}

## 11. 待确认清单

- [ ] 目标地域与可用区
- [ ] 合规框架（等保 / ISO27001 / SOC2 等）
- [ ] 网络互联方式与带宽
- [ ] 数据与驻留要求

---

## 附录 E AWS专有口径

**E.1 目标端平台基线**（专有服务名按官方写法，不臆造 / 不翻译）

| 领域 | AWS 基线 |
|---|---|
| 账号与组织架构 | AWS Organizations + Control Tower；OU 结构（Security / Log Archive / Shared Services / Workloads）；SCP 护栏；Consolidated Billing 与成本分配标签 |
| 网络架构 | VPC + Subnet（public / private / isolated 三层）；Transit Gateway 做多账号互联；Direct Connect + Site-to-Site VPN 冗余；ALB / NLB；NAT Gateway；Route 53 |
| 安全与合规 | GuardDuty / Security Hub / Inspector；WAF + Shield；KMS；Config 规则；CloudTrail Organization Trail；IAM Access Analyzer；合规框架映射（由甲方确定适用项） |
| 身份与访问（IAM） | IAM roles / users / policies；IAM Identity Center（SSO）；Permission Boundary；跨账号 Role 承担；SCP 约束 |
| 计算 | EC2 实例族（m7i / c7i / r7i，以目标 Region 实际可用为准）；Auto Scaling Group；EKS；Launch Template + AMI |
| 存储 | S3（Standard / IA / Glacier）；EBS gp3 / io2；EFS；S3 Replication；Lifecycle 策略 |
| 数据库 | RDS / Aurora；DynamoDB；ElastiCache；DMS（迁移 + CDC + 校验）；Redshift |
| 监控与运维 | CloudWatch（Metrics / Logs / Alarms）；CloudTrail；X-Ray；EventBridge 告警路由；SNS 通知 |

**E.2 迁移工具与方式**
- 主机迁移：Application Migration Service（MGN）
- 数据库迁移：Database Migration Service（DMS）+ 一致性校验任务
- 数据迁移：DataSync / Snowball（大体量离线）
- 评估与规划：Migration Hub + Application Discovery Service
- IaC / 编排：CloudFormation / CDK 或 Terraform（AWS Provider）

**E.3 验收口径**
- 账号体系与护栏符合《AWS Landing Zone / Control Tower 基线》双方确认版
- 专有名词不翻译：VPC / EC2 / S3 / IAM / DMS / EKS / CloudWatch
- 安全合规基线由乙方提供配置项，审计结论归甲方

**E.4 商务口径**
- AWS 资源费用由甲方与 AWS 侧结算，不含在本服务金额内
- 服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算依据

**E.5 色系与证据**
- `--brand aws` → 主色 `232F3E`，表头底 `232F3E`，正文 `333333`
- 色值来源：Veolia-AWS Landing Zone Design-LLD-English-V2.3.docx: 16191F x32, 000000, FFFFFF, 333333
