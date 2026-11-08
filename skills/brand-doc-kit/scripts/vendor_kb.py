# -*- coding: utf-8 -*-
"""厂家专有基线知识库（单一事实源）。

用途：报价单 / HLD / LLD / 投标技术标 生成厂家变体文档时，提供
「服务名基线 / 迁移工具 / 验收口径 / 商务口径 / IaC 工具」四类专有事实。
色值一律取自 brand_profiles/<brand>.json，本文件不重复定义色值。

维护纪律（重要）：
- 服务名按厂家官方写法，不臆造、不翻译（ECS / OSS / CEN / RAM 保持原文）。
- 新增厂家：复制一段字典，逐项填官方服务名；禁止跨厂家串用服务名。
"""

# 8 大领域：与 pcs-hld 的领域划分一致（账号与组织/网络/安全与合规/IAM/计算/存储/数据库/监控运维）
DOMAIN_ORDER = [
    ("账号与组织架构", "account"),
    ("网络架构", "network"),
    ("安全与合规", "security"),
    ("身份与访问（IAM）", "iam"),
    ("计算", "compute"),
    ("存储", "storage"),
    ("数据库", "database"),
    ("监控与运维", "monitor"),
]

VENDOR_KB = {
    "alibaba": {
        "label": "阿里橙",
        "vendor": "阿里云",
        "domains": {
            "account": "资源目录 / 资源管理 多账号结构（管理账号 + 成员账号）；资源组与标签分账；共享服务账号承载日志审计与网络"
                "；Landing Zone 基线以双方确认版为准",
            "network": "VPC + 交换机（VSwitch）按环境/分层划分；云企业网 CEN 做多地域互联；高速通道 / VPN 网关做混合云接入"
                "；SLB / ALB 承载入口流量；NAT 网关统一出网",
            "security": "云防火墙 / WAF / 云安全中心（安骑士）/ KMS / DDoS 高防；操作审计 ActionTrail + 配置审计做合规留痕"
                "；等保 2.0 三级基线由乙方提供配置项，测评结论归甲方",
            "iam": "RAM 用户 / 角色 / 策略；STS 临时凭证；跨账号 RAM 角色授权；权限边界与最小权限矩阵",
            "compute": "ECS 实例规格族（通用型 g7 / 计算型 c7 / 内存型 r7）；弹性伸缩 ESS；ACK 承载容器化负载",
            "storage": "OSS（标准 / 低频 / 归档）；NAS 共享文件存储；ESSD 块存储；跨区域复制与生命周期策略",
            "database": "RDS MySQL / PostgreSQL；PolarDB 集群版；ADB 分析型；Redis / Tair 缓存；DTS 做同步与一致性校验",
            "monitor": "云监控 + SLS 日志服务 + ARMS 应用监控；告警联系人与行动策略；备份策略与恢复演练",
        },
        "migration_tools": [
            "主机迁移：SMC（服务器迁移中心），源端安装 SMC 客户端后做镜像/增量同步",
            "数据库迁移：DTS（结构迁移 + 全量 + 增量 + 校验）",
            "数据/大数据迁移：DataWorks / MaxCompute 侧目标端架构责任方需在责任矩阵中写明",
        ],
        "acceptance": [
            "账号体系与权限基线符合《阿里云 Landing Zone 基线》双方确认版",
            "专有名词不翻译：ECS / OSS / VPC / CEN / RAM / DTS / SMC / SLS",
            "等保合规：乙方提供配置基线及整改建议，不承担测评结论",
        ],
        "commercial": [
            "云资源费用（包年包月 / 按量 / PHA）由甲方与阿里云侧结算，不含在本服务金额内",
            "服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算、签到、出勤验收依据",
        ],
        "iac": "ROS（资源编排）或 Terraform（阿里云 Provider）",
        "spec_hint": "实例规格与数据库型号须以目标地域实际可购买为准，Mock/模板值必须人工复核",
    },
    "tencent": {
        "label": "腾讯蓝",
        "vendor": "腾讯云",
        "domains": {
            "account": "组织 Organizations 多账号结构（集团账号 / 成员账号）；标签分账与成本归集；共享服务账号承载日志与网络",
            "network": "VPC + 子网按环境隔离；云联网 CCN 做多地域互联；专线接入 / Direct Connect / VPN 网关做混合云"
                "；CLB 承载入口流量；NAT 网关统一出网；对等连接做 VPC 互通",
            "security": "云防火墙 / Web 应用防火墙 WAF / 主机安全 CWP / KMS / DDoS 防护；云审计 CloudAudit 留痕"
                "；等保 2.0 三级基线由乙方提供配置项，测评结论归甲方",
            "iam": "CAM 用户 / 角色 / 策略；子账号与协作者；STS 临时凭证；消息接收人配置",
            "compute": "CVM 实例族（标准型 S5 / SA3，按压测调整）；弹性伸缩 AS；TKE 容器服务承载容器化负载",
            "storage": "COS 存储桶（标准 / 低频 / 归档）；CFS 文件存储；CBS 云硬盘（SSD / 增强型 SSD）；跨地域复制与生命周期",
            "database": "TencentDB MySQL / PostgreSQL；TDSQL 分布式；云数据库 Redis；DTS 数据传输服务做同步与校验",
            "monitor": "云监控 CM + 日志服务 CLS + 应用性能观测 APM；告警策略与接收组；备份与恢复演练",
        },
        "migration_tools": [
            "主机迁移：在线迁移工具 / 离线镜像导入（按源端形态选型）",
            "数据库迁移：DTS 数据传输服务（结构 + 全量 + 增量 + 一致性校验）",
            "对象存储迁移：COS 迁移工具 / MSCP",
        ],
        "acceptance": [
            "账号体系与权限基线符合《腾讯云 Landing Zone 基线》双方确认版",
            "专有名词不翻译：CVM / COS / CCN / CAM / CLB / TKE / CLS",
            "等保合规：乙方提供配置基线及整改建议，不承担测评结论",
        ],
        "commercial": [
            "云资源费用由甲方与腾讯云侧结算，不含在本服务金额内",
            "服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算依据",
        ],
        "iac": "Terraform（腾讯云 Provider）或 TIC 资源编排",
        "spec_hint": "实例规格与数据库型号须以目标地域实际可购买为准，Mock/模板值必须人工复核",
    },
    "anchnet": {
        "label": "安畅红",
        "vendor": "安畅（中立 MSP 口径）",
        "domains": {
            "account": "按目标云约定建立账号 / 订阅体系；管理账号与业务账号分离；标签与分账规则先行；根账号由甲方持有",
            "network": "地址规划与网段分配表；跨地域互联方案依目标云选型；专线 / VPN 双链路冗余；出网与 NAT 集中管控",
            "security": "边界防护 / WAF / 主机安全 / 密钥管理；安全基线与加固清单；等保与合规整改建议（不承担测评结论）",
            "iam": "最小权限角色矩阵；人机分离（运维账号 / 程序账号）；临时凭证；季度权限复核",
            "compute": "实例族选型与容量规划；伸缩组与弹性策略；容器平台依目标云选型；黄金镜像管理",
            "storage": "对象 / 文件 / 块存储分层；生命周期与跨区域复制；静态加密与密钥托管",
            "database": "引擎与版本选型；高可用架构（主备 / 集群）；迁移工具与一致性校验；缓存层设计",
            "monitor": "指标 / 日志 / 链路三类采集；告警分级与值班机制；备份与恢复演练；移交运维手册",
        },
        "migration_tools": [
            "主机迁移：按源端与目标云选型，优先目标云官方迁移服务",
            "数据库迁移：官方数据传输服务 + 停机窗口内增量追平 + Count/MD5 校验",
            "割接：分批分波次，每套系统单独验证与回退预案",
        ],
        "acceptance": [
            "以《迁移系统范围清单（调研确认版）》为唯一范围基线，各章节数字必须一致",
            "每套系统须：迁移验证 + 数据完整性确认 + 功能验证通过 + 双方确认割接完成",
            "交付物经甲方书面 / 在线确认即视为该阶段验收通过",
        ],
        "commercial": [
            "云资源费用由甲方向云厂商直接结算，不含在本服务金额内",
            "第三方 License 由甲方承担；范围外工作走 PCR 变更",
        ],
        "iac": "Terraform（云中立写法，按目标云切换 Provider）",
        "spec_hint": "中性写法不绑定单一厂家服务名；涉及具体厂家时引用对应厂家变体文档",
    },
    "aws": {
        "label": "AWS黑",
        "vendor": "AWS",
        "domains": {
            "account": "AWS Organizations + Control Tower；OU 结构（Security / Log Archive / Shared Services / Workloads）"
                "；SCP 护栏；Consolidated Billing 与成本分配标签",
            "network": "VPC + Subnet（public / private / isolated 三层）；Transit Gateway 做多账号互联"
                "；Direct Connect + Site-to-Site VPN 冗余；ALB / NLB；NAT Gateway；Route 53",
            "security": "GuardDuty / Security Hub / Inspector；WAF + Shield；KMS；Config 规则；CloudTrail Organization Trail"
                "；IAM Access Analyzer；合规框架映射（由甲方确定适用项）",
            "iam": "IAM roles / users / policies；IAM Identity Center（SSO）；Permission Boundary；跨账号 Role 承担；SCP 约束",
            "compute": "EC2 实例族（m7i / c7i / r7i，以目标 Region 实际可用为准）；Auto Scaling Group；EKS；Launch Template + AMI",
            "storage": "S3（Standard / IA / Glacier）；EBS gp3 / io2；EFS；S3 Replication；Lifecycle 策略",
            "database": "RDS / Aurora；DynamoDB；ElastiCache；DMS（迁移 + CDC + 校验）；Redshift",
            "monitor": "CloudWatch（Metrics / Logs / Alarms）；CloudTrail；X-Ray；EventBridge 告警路由；SNS 通知",
        },
        "migration_tools": [
            "主机迁移：Application Migration Service（MGN）",
            "数据库迁移：Database Migration Service（DMS）+ 一致性校验任务",
            "数据迁移：DataSync / Snowball（大体量离线）",
            "评估与规划：Migration Hub + Application Discovery Service",
        ],
        "acceptance": [
            "账号体系与护栏符合《AWS Landing Zone / Control Tower 基线》双方确认版",
            "专有名词不翻译：VPC / EC2 / S3 / IAM / DMS / EKS / CloudWatch",
            "安全合规基线由乙方提供配置项，审计结论归甲方",
        ],
        "commercial": [
            "AWS 资源费用由甲方与 AWS 侧结算，不含在本服务金额内",
            "服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算依据",
        ],
        "iac": "CloudFormation / CDK 或 Terraform（AWS Provider）",
        "spec_hint": "实例族 / 数据库型号须按目标 Region 实际可购买清单复核，禁止沿用模板值",
    },
    "azure": {
        "label": "Azure浅蓝",
        "vendor": "Microsoft Azure",
        "domains": {
            "account": "Management Group 层次 + Subscription 划分；Azure Policy 与蓝图做基线护栏；RBAC 继承设计"
                "；计费账户（EA / MCA）与成本分摊标签",
            "network": "Virtual Network + Subnet 分层；vWAN / ExpressRoute 做多地域与混合互联；VPN Gateway 冗余"
                "；Azure Firewall；Application Gateway；NSG / ASG；Private Link",
            "security": "Microsoft Defender for Cloud；Sentinel；Key Vault；DDoS Protection；Azure Policy 合规基线"
                "；合规管理器映射（由甲方确定适用项）",
            "iam": "Entra ID（原 Azure AD）；RBAC 角色分配；PIM 特权身份管理；Managed Identity；Conditional Access",
            "compute": "VM / Virtual Machine Scale Sets，规格族（D / E / F 系列）；AKS；App Service；可用性区与可用性集",
            "storage": "Blob（Hot / Cool / Archive）；Managed Disk（Premium SSD / Ultra）；Azure Files；生命周期管理",
            "database": "Azure SQL / SQL Managed Instance；Azure Database for MySQL / PostgreSQL；Cosmos DB"
                "；Azure Database Migration Service（DMS）",
            "monitor": "Azure Monitor + Log Analytics + Application Insights；Action Group / Alert Rule；备份与 Site Recovery",
        },
        "migration_tools": [
            "评估与迁移：Azure Migrate（发现评估 + 服务器迁移 + 数据库迁移）",
            "数据库迁移：Database Migration Service（DMS）/ Data Migration Assistant",
            "数据迁移：Data Box / AzCopy / Data Factory",
        ],
        "acceptance": [
            "订阅与治理基线符合《Azure Landing Zone（CAF）基线》双方确认版",
            "专有名词不翻译：VNet / AKS / Entra ID / ExpressRoute / Azure SQL / Log Analytics",
            "合规基线由乙方提供配置项，审计结论归甲方",
        ],
        "commercial": [
            "Azure 资源费用由甲方与微软侧 / CSP 结算，不含在本服务金额内",
            "服务包模式：人天 / 人月仅作能力与工作量评估依据，不作为结算依据",
        ],
        "iac": "Bicep / ARM 模板或 Terraform（AzureRM Provider）",
        "spec_hint": "VM 规格族与数据库型号须按目标 Region 实际可购买清单复核",
    },
}

BRAND_ORDER = ["alibaba", "tencent", "anchnet", "aws", "azure"]

# 各文档类型在文件命名中的后缀（与 SOW 模板命名保持一致：SOW模板_阿里橙.md）
DOC_TYPES = {
    "quotation": {"suffix": "报价单", "title": "迁移服务报价单"},
    "hld": {"suffix": "HLD", "title": "高级架构设计（HLD）"},
    "lld": {"suffix": "LLD", "title": "详细架构设计（LLD）"},
    "bid": {"suffix": "投标技术标", "title": "投标技术方案书"},
}


def get_vendor(brand: str) -> dict:
    """按 brand key 返回厂家知识库条目；未知 key 直接抛错（禁止静默回退）。"""
    if brand not in VENDOR_KB:
        raise SystemExit(
            f"未知厂家 key: {brand}（可用: {', '.join(BRAND_ORDER)}）"
        )
    return VENDOR_KB[brand]
