# {{客户名}} {{项目名}} 迁移服务报价单（AWS黑）

> 色系皮肤：`--brand aws`（渲染时由 `scripts/build_docx.py` 套用 AWS 品牌色）

> 版本：v{{N}} ｜ 日期：{{date}} ｜ 币种：{{CNY|USD}}
> 单价基准：$350/人天（AC-MIG）｜ 有效期：{{30}} 天
> 目标云：**AWS**
> 状态：{{draft|final}}

---

## 一、计价假设

| 项 | 取值 | 来源 |
|---|---|---|
| 单价（人天） | $350 | AC-MIG 基准 |
| 目标云 | AWS | 项目信息表 |
| 项目类型 | {{新建/迁移/改造}} | 项目信息表 |
| 复杂度系数 | {{1.0 / 1.2 / 1.5}} | 评估报告 |
| 多区域标志 | {{是/否}} | 项目信息表 |
| 异构数据库标志 | {{是/否}} | 评估报告 |
| 交付语言 | {{中/英/双语}} | 项目信息表 |

> 未确认项一律不臆造，列入「五、待确认清单」。

## 二、角色 × 人天明细

| # | 角色 | 工作内容 | 人天 | 单价 | 小计 |
|---|---|---|---|---|---|
| 1 | {{角色}} | {{内容}} | {{n}} | 350 | {{n×350}} |
| … | | | | | |
| | **合计** | | **{{总人天}}** | | **{{总金额}}** |

> 角色池：PM · 云架构师 · 云工程师（计算及存储）· 迁移工程师（中间件）· 数据库工程师 · 大数据工程师 · 安全架构师 · {{专项实施方}}团队

## 三、加计项

| 项 | 触发条件 | 加计比例 | 金额 |
|---|---|---|---|
| 多区域 | 跨 ≥2 地域 | {{}} | |
| 异构数据库 | 跨引擎迁移 | {{}} | |
| 风险储备 | 复杂度 ≥1.2 | {{}} | |

## 四、总计

| 项 | 金额 |
|---|---|
| 人天小计 | {{}} |
| 加计合计 | {{}} |
| **合同金额** | **{{}}** |

> 校验：人天 × 单价 = 小计，各行小计之和 = 总计。
> 执行 `scripts/validate_quote.py` 自动校验，失败不得出稿。

## 五、待确认清单

- [ ] RTO / RPO
- [ ] 停机窗口
- [ ] 数据增量
- [ ] 第三方 License
- [ ] 等保 / 合规要求
- [ ] 目标地域与可用区清单

## 六、不含项

- 云资源费用（由甲方与AWS侧直接结算）
- 第三方软件 License
- 甲方人员配合成本
- 超出约定轮次的方案返工

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
