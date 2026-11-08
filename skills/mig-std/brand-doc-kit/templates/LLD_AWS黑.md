# {{客户名}} {{项目名}} 详细架构设计（LLD）（AWS黑）

> 色系皮肤：`--brand aws`（渲染时由 `scripts/build_docx.py` 套用 AWS 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 密级：L2-内部级
> 目标云：**AWS** ｜ 目标地域：{{region}}
> 前置：本文件的输入是 HLD（未产出 HLD 时不得启动，参数无法落地）
> 参考域名基线：AWS｜账号：AWS Organizations + Control Tower；OU 结构（…｜网络：VPC + Subnet（public / private / isolated…

---

## 1. 网络拓扑与地址规划

**1.1 地址规划表**

| VPC / VNet | 网段 CIDR | 用途 | 子网 CIDR | 可用区 | 说明 |
|---|---|---|---|---|---|
| {{名称}} | {{10.x.0.0/16}} | {{生产/测试/共享}} | {{10.x.1.0/24}} | {{az-a}} | |

**1.2 路由表**：{{每条写：目标网段 → 下一跳 → 说明}}
**1.3 互联**：{{专线 / VPN / 云联网，按 AWS 服务实现}}
**1.4 安全组 / 防火墙规则矩阵**

| 源 | 目的 | 端口 | 协议 | 动作 | 依据 |
|---|---|---|---|---|---|

> 规则必须有依据列；写「全通 / 0.0.0.0/0 全放」须注明甲方书面确认。

## 2. 计算实例规格表

| 主机名 | 用途 | 实例规格 | vCPU | 内存 | 系统盘 | 数据盘 | 数量 |
|---|---|---|---|---|---|---|---|
| {{}} | | {{按目标地域实际可购买清单}} | | | | | |

> **规格真实性红线**：实例族 / 数据库型号须按目标 Region 实际可购买清单复核，禁止沿用模板值

## 3. 数据库规格表

| 实例名 | 引擎与版本 | 规格 | 存储 | 高可用 | 备份策略 | 备注 |
|---|---|---|---|---|---|---|

## 4. 存储设计

| 存储类型 | 容量 | 访问模式 | 生命周期 | 加密 |
|---|---|---|---|---|

> 参考基线（AWS）：S3（Standard / IA / Glacier）；EBS gp3 / io2；EFS；S3 Replication；Lifecycle 策略

## 5. 安全与合规清单

| # | 检查项 | 基线要求 | 当前状态 | 责任人 |
|---|---|---|---|---|

> 参考基线（AWS）：GuardDuty / Security Hub / Inspector；WAF + Shield；KMS；Config 规则；CloudTrail Organization Trail；IAM Access Analyzer；合规框架映射（由甲方确定适用项）
> 身份与访问：IAM roles / users / policies；IAM Identity Center（SSO）；Permission Boundary；跨账号 Role 承担；SCP 约束

## 6. 监控与告警配置

| 监控对象 | 指标 / 日志源 | 阈值 | 告警级别 | 通知方式 |
|---|---|---|---|---|

> 参考基线（AWS）：CloudWatch（Metrics / Logs / Alarms）；CloudTrail；X-Ray；EventBridge 告警路由；SNS 通知

## 7. 部署步骤（IaC）

- 编排工具：**CloudFormation / CDK 或 Terraform（AWS Provider）**
- 目录结构：{{modules / environments / variables}}
- 执行顺序：{{网络 → 安全 → 计算 → 数据 → 监控}}
- 回滚方式：{{按栈销毁 / 版本回退}}

> 部署步骤里的资源规格必须人工核对是否真实存在（模板值与 Mock 值常见）。

## 8. 待确认清单

- [ ] 网段与甲方现网是否冲突
- [ ] 实例规格在目标地域的可购买性
- [ ] 数据库版本兼容性
- [ ] 安全规则例外项

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
