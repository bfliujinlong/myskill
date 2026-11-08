#!/usr/bin/env python3
"""云迁移交付编排 / Delivery Orchestration（阶段 04 实施）

用法:
    python3 delivery_orch.py --self-test
    python3 delivery_orch.py --input orch.json --out-dir ./out

输入 JSON:
{
  "project": "C-Customer CHINA M2C",        # 必填
  "track": "business-migration",            # 必填: business-migration|landing-zone|bigdata-migration|well-architected
  "start_date": "2026-11-03",               # 选填（有则按工作日排期，跳过周末）
  "hours_per_day": 8,                       # 选填，默认 8
  "team_size": 2,                           # 选填，默认 2（并行人数，影响日历日）
  "done": ["A-001","A-002"],                # 选填：已完成 Action（看板回填）
  "blocked": [{"id":"A-035","reason":"专线未通"}],   # 选填：阻塞项
  "extra_actions": [{"id":"A-100","name":"...","phase":"实施部署","trigger":"manual","hours":4,"priority":"high","depends_on":["A-034"]}],
  "depends_on": {"A-035":["A-034"]},        # 选填：额外依赖（前置 -> 本项）
  "scale": 1.0                              # 选填：工时缩放（应用数/数据量>基线时上调，默认 1.0）
}

输出: delivery_orch.md（可读）+ delivery_orch.json（结构化）

设计口径:
- Action 库来自客户执行计划看板真表，**不臆造任务**；未知 track/未知 action id 直接报错。
- 排期：按阶段顺序 + 显式依赖；无 start_date 只出工时与关键路径，不出日历日（不编造日期）。
- 门禁：每个阶段末自动插一条 gate（阶段出口检查），缺验收判据时标「待确认」，不伪造。
- 红线: 本脚本**不输出任何金额/单价/人天单价**；只出工时（h）与工期（日历日/工作日）。
          备注：工时≠报价，报价一律由 pcs-quotation 出具。
退出码: 0 = 正常；2 = 输入不可用/必填缺失
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# 交付编排 Action 库：来自客户执行计划看板真表（020BF534 业务迁移/LandingZone/大数据迁移/Well-Architected）
# 字段: (id, 名称, 阶段, 触发 manual/auto/doc, 工时h, 优先级 high/med/low)
TRACKS: dict[str, dict] = {
    "business-migration": {"cn": "业务迁移", "prefix": "A", "actions": [
        ("A-001", "客户业务需求初步对接（核心场景/痛点/目标）", "售前对接", "manual", 2, "high"),
        ("A-002", "迁移可行性预评估（技术/成本/周期初步判断）", "售前对接", "manual", 2, "high"),
        ("A-003", "云厂商/技术方案初稿输出", "售前对接", "manual", 2, "med"),
        ("A-004", "客户技术答疑与方案沟通", "售前对接", "manual", 2, "med"),
        ("A-005", "项目报价与合同谈判支持", "售前对接", "manual", 2, "med"),
        ("A-006", "确定项目组织架构与干系人，明确目标/范围/里程碑", "售前对接", "manual", 2, "high"),
        ("A-007", "项目明道立项", "明道立项", "manual", 1, "high"),
        ("A-008", "业务需求调研（业务流程/峰值流量/合规要求）", "信息调研", "manual", 2, "high"),
        ("A-009", "源环境IT资产调研（服务器/数据库/中间件/存储）", "信息调研", "manual", 2, "high"),
        ("A-010", "源环境网络拓扑调研（网段/CIDR/路由/安全策略）", "信息调研", "manual", 2, "high"),
        ("A-011", "数据资产调研（数据量/表结构/读写频率/敏感数据）", "信息调研", "manual", 2, "med"),
        ("A-012", "应用架构调研（应用依赖/部署架构/技术栈版本）", "信息调研", "manual", 2, "med"),
        ("A-013", "调研信息梳理（资产/需求/架构数据标准化归类）", "信息调研", "manual", 2, "med"),
        ("A-014", "目标云技术架构图绘制（网络/应用/数据/安全/监控分层）", "方案设计", "manual", 4, "high"),
        ("A-015", "网络/专线/VPN方案确认与资源采购流程梳理", "方案设计", "manual", 8, "high"),
        ("A-016", "VPC及子网精细化规划（按业务模块/安全级别/可用区）", "方案设计", "manual", 1, "med"),
        ("A-017", "云资源容量规划（服务器/数据库/存储/带宽规格选型）", "方案设计", "manual", 1, "med"),
        ("A-018", "数据迁移方案规划（全量/增量迁移策略+工具选型）", "方案设计", "manual", 1, "high"),
        ("A-019", "应用迁移方案规划（直接迁移/重构/容器化改造策略）", "方案设计", "manual", 1, "med"),
        ("A-020", "安全架构规划（权限模型/数据加密/安全组/审计方案）", "方案设计", "manual", 1, "high"),
        ("A-021", "迁移项目计划规划（里程碑/阶段划分/责任分工/时间窗）", "方案设计", "manual", 1, "high"),
        ("A-022", "迁移风险评估与应急预案制定（含回滚方案）", "方案设计", "manual", 1, "high"),
        ("A-023", "三方迁移方案评审会议", "方案评审", "manual", 4, "high"),
        ("A-024", "目标云主账号开通及实名认证", "POC验证", "manual", 4, "high"),
        ("A-025", "IAM子账号创建及最小权限配置", "POC验证", "manual", 1, "high"),
        ("A-026", "VPC/安全组创建与配置", "POC验证", "manual", 1, "high"),
        ("A-027", "RDS实例开通与初始化配置", "POC验证", "manual", 2, "med"),
        ("A-028", "ECS服务器创建与基础配置", "POC验证", "manual", 2, "med"),
        ("A-029", "DTS全量迁移任务配置与启动", "POC验证", "auto", 2, "high"),
        ("A-030", "DTS增量同步配置（binlog/CDC）", "POC验证", "auto", 2, "high"),
        ("A-031", "SMS主机迁移接入与配置", "POC验证", "auto", 2, "med"),
        ("A-032", "UAT业务功能验证（核心业务流程测试）", "POC验证", "manual", 4, "high"),
        ("A-033", "UAT数据一致性验证（count/MD5校验）", "POC验证", "auto", 2, "high"),
        ("A-034", "生产主账号开通及IAM配置", "实施部署", "manual", 4, "high"),
        ("A-035", "生产VPC/安全组/路由表创建", "实施部署", "manual", 2, "high"),
        ("A-036", "生产RDS实例开通与高可用配置", "实施部署", "manual", 2, "high"),
        ("A-037", "生产ECS服务器批量创建与配置", "实施部署", "manual", 4, "high"),
        ("A-038", "生产数据全量迁移执行（DTS）", "实施部署", "auto", 8, "high"),
        ("A-039", "生产增量数据同步（DTS增量binlog）", "实施部署", "auto", 4, "high"),
        ("A-040", "生产业务联调验证（PRD可用性验证）", "实施部署", "manual", 4, "high"),
        ("A-041", "正式割接操作（按割接checklist逐项执行）", "割接上线", "manual", 8, "high"),
        ("A-042", "割接后业务验证（全链路功能回归测试）", "割接上线", "manual", 4, "high"),
        ("A-043", "测试资源释放（POC/UAT环境资源清理）", "交付收尾", "manual", 1, "low"),
        ("A-044", "《项目验收报告》编写与客户确认", "交付收尾", "doc", 2, "high"),
        ("A-045", "项目复盘与经验总结", "交付收尾", "manual", 2, "med"),
        ("A-046", "交付邮件发送", "交付收尾", "manual", 1, "high"),
    ]},
    "landing-zone": {"cn": "LandingZone", "prefix": "L", "actions": [
        ("L-001", "客户业务需求初步对接（LZ整体诉求/云战略目标）", "售前对接", "manual", 2, "high"),
        ("L-002", "项目明道立项", "明道立项", "manual", 1, "high"),
        ("L-003", "账号体系现状调研（账号数量/层级/Owner分布）", "需求调研", "manual", 2, "high"),
        ("L-004", "资源规划需求调研（VPC/Region/可用区/账号隔离）", "需求调研", "manual", 2, "high"),
        ("L-005", "网络规划调研（专线/VPN/Transit Gateway/对等连接）", "需求调研", "manual", 2, "high"),
        ("L-006", "身份权限调研（SSO集成/RAM角色/最小权限策略）", "需求调研", "manual", 2, "high"),
        ("L-007", "安全防护调研（WAF/CFW/DDoS/数据加密/审计要求）", "需求调研", "manual", 2, "med"),
        ("L-008", "财务管理调研（多账号付款模式/成本分配/预算控制）", "需求调研", "manual", 2, "med"),
        ("L-009", "合规审计调研（操作审计/配置审计/管控策略/法规）", "需求调研", "manual", 2, "med"),
        ("L-010", "运维管理调研（监控/告警/日志/自动化运维需求）", "需求调研", "manual", 2, "med"),
        ("L-011", "IaC自动化需求调研（Terraform模块规划）", "需求调研", "manual", 2, "high"),
        ("L-012", "账号体系与资源夹结构设计（多账号层级规划）", "方案设计", "manual", 4, "high"),
        ("L-013", "网络架构HLD设计（Transit VPC/Hub-Spoke拓扑）", "方案设计", "manual", 4, "high"),
        ("L-014", "网络LLD设计（VPC/子网/路由表/安全组详细规划）", "方案设计", "manual", 4, "high"),
        ("L-015", "身份权限方案设计（SSO/RAM角色/权限边界设计）", "方案设计", "manual", 4, "high"),
        ("L-016", "安全防护方案设计（云上安全产品选型与配置策略）", "方案设计", "manual", 4, "high"),
        ("L-017", "财务管理方案设计（多账号付款/标签分账/预算告警）", "方案设计", "manual", 3, "med"),
        ("L-018", "合规审计方案设计（操作审计/配置审计/管控策略SCP）", "方案设计", "manual", 3, "med"),
        ("L-019", "运维管理方案设计（云监控/日志服务/运维自动化）", "方案设计", "manual", 3, "med"),
        ("L-020", "Terraform模块规划与IaC架构设计", "方案设计", "manual", 4, "high"),
        ("L-021", "LandingZone HLD评审（与客户/云厂商三方评审）", "HLD评审", "manual", 4, "high"),
        ("L-022", "LandingZone LLD评审（详细设计确认）", "HLD评审", "manual", 4, "high"),
        ("L-023", "管理账号初始化（账号开通/组织创建/资源夹配置）", "实施部署", "manual", 4, "high"),
        ("L-024", "成员账号批量创建（OU划分/账号命名规范）", "实施部署", "manual", 2, "high"),
        ("L-025", "Transit VPC创建与互联配置", "实施部署", "manual", 4, "high"),
        ("L-026", "各账号VPC/子网/路由表创建", "实施部署", "manual", 4, "high"),
        ("L-027", "SSO单点登录配置（与企业IdP集成）", "实施部署", "manual", 4, "high"),
        ("L-028", "RAM角色与权限策略批量配置", "实施部署", "manual", 2, "high"),
        ("L-029", "云防火墙/WAF/DDoS防护开启配置", "实施部署", "manual", 2, "med"),
        ("L-030", "多账号付款模式配置（主账号代付）", "实施部署", "manual", 1, "low"),
        ("L-031", "成本标签策略配置（资源标签+费用分摊）", "实施部署", "manual", 2, "med"),
        ("L-032", "操作审计（CloudTrail/ActionTrail）部署", "实施部署", "manual", 1, "med"),
        ("L-033", "配置审计规则配置（合规包部署）", "实施部署", "manual", 2, "med"),
        ("L-034", "管控策略SCP配置与绑定", "实施部署", "manual", 2, "high"),
        ("L-035", "云监控告警规则配置（关键指标/阈值/通知渠道）", "实施部署", "manual", 2, "med"),
        ("L-036", "编写Terraform/IaC模板（按HLD模块化编写）", "IaC自动化", "manual", 8, "high"),
        ("L-037", "执行自动化部署流水线（CI/CD触发全量资源创建）", "IaC自动化", "auto", 4, "high"),
        ("L-038", "验证各账号基础配置一致性（自动化脚本校验）", "IaC自动化", "auto", 2, "high"),
        ("L-039", "测试资源释放", "交付收尾", "manual", 1, "low"),
        ("L-040", "《项目验收报告》+《LZ调研表》整理", "交付收尾", "doc", 2, "high"),
        ("L-041", "交付邮件发送", "交付收尾", "manual", 1, "high"),
    ]},
    "bigdata-migration": {"cn": "大数据迁移", "prefix": "B", "actions": [
        ("B-001", "客户业务需求初步对接（大数据场景/痛点/目标）", "售前对接", "manual", 2, "high"),
        ("B-002", "迁移可行性预评估（组件兼容性/数据量/成本）", "售前对接", "manual", 2, "high"),
        ("B-003", "项目明道立项", "明道立项", "manual", 1, "high"),
        ("B-004", "Hadoop版本/组件清单调研（HDFS/Yarn/Hive/HBase）", "信息调研", "manual", 2, "high"),
        ("B-005", "节点规格/数量调研（DataNode/NameNode/磁盘类型）", "信息调研", "manual", 2, "high"),
        ("B-006", "数据量及增量速率调研（总量TB/每日增量GB）", "信息调研", "manual", 2, "high"),
        ("B-007", "网络带宽限制调研（IDC到目标云专线带宽）", "信息调研", "manual", 1, "med"),
        ("B-008", "敏感数据识别与分级调研（PII/财务/行为数据）", "信息调研", "manual", 1, "med"),
        ("B-009", "调度系统调研（Airflow/DolphinScheduler版本）", "信息调研", "manual", 2, "med"),
        ("B-010", "实时计算组件调研（Flink/Spark Streaming/Kafka）", "信息调研", "manual", 2, "med"),
        ("B-011", "目标集群架构设计（Master/Core/Task节点规格选型）", "方案设计", "manual", 4, "high"),
        ("B-012", "数据分层存储方案设计（热温冷数据分层策略）", "方案设计", "manual", 2, "med"),
        ("B-013", "Hive Metastore迁移方案（元数据库选型及迁移策略）", "方案设计", "manual", 2, "high"),
        ("B-014", "调度任务迁移方案（任务改造适配及双跑策略）", "方案设计", "manual", 2, "high"),
        ("B-015", "数据迁移工具选型（Distcp/DataX/自研工具对比）", "方案设计", "manual", 2, "high"),
        ("B-016", "数据校验方案设计（count/MD5/业务指标三级校验）", "方案设计", "manual", 2, "high"),
        ("B-017", "目标集群创建及基础配置（节点规格/网络/存储）", "工具部署", "manual", 4, "high"),
        ("B-018", "组件安装与版本配置（CDH/EMR/自建集群）", "工具部署", "manual", 4, "high"),
        ("B-019", "调度系统迁移部署（任务导出/导入/适配改造）", "工具部署", "manual", 8, "high"),
        ("B-020", "调度任务语法适配（SQL方言/UDF/自定义函数改造）", "工具部署", "manual", 8, "high"),
        ("B-021", "数据迁移工具部署与配置（Distcp/DataX参数调优）", "工具部署", "auto", 2, "med"),
        ("B-022", "Hive Metastore元数据迁移执行", "数据迁移", "auto", 4, "high"),
        ("B-023", "元数据迁移结果验证（表数量/分区数/Schema一致性）", "数据迁移", "auto", 2, "high"),
        ("B-024", "存量数据全量迁移（Distcp执行+进度监控）", "数据迁移", "auto", 8, "high"),
        ("B-025", "增量数据同步配置（Kafka/Canal/CDC工具）", "数据迁移", "auto", 4, "high"),
        ("B-026", "全量数据count校验（源/目标行数对比）", "数据校验", "auto", 2, "high"),
        ("B-027", "增量数据count校验（按时间窗口抽样对比）", "数据校验", "auto", 2, "high"),
        ("B-028", "MD5哈希抽样校验（关键表字段级别一致性验证）", "数据校验", "auto", 4, "high"),
        ("B-029", "调度任务双跑启动（源/目标环境同时运行）", "双跑验证", "manual", 4, "high"),
        ("B-030", "双跑结果对比验证（关键指标/数据质量对比报告）", "双跑验证", "manual", 8, "high"),
        ("B-031", "割接窗口执行（停写源端→切流→验证→观察）", "割接上线", "manual", 8, "high"),
        ("B-032", "测试资源释放", "割接上线", "manual", 1, "low"),
        ("B-033", "《项目验收报告》编写", "割接上线", "doc", 2, "high"),
        ("B-034", "交付邮件发送", "割接上线", "manual", 1, "high"),
    ]},
    "well-architected": {"cn": "Well-Architected", "prefix": "W", "actions": [
        ("W-001", "客户业务需求初步对接（WA改造诉求/合规背景）", "售前对接", "manual", 2, "high"),
        ("W-002", "明确SOW实施范围（5模块选择/优先级确认）", "售前对接", "manual", 2, "high"),
        ("W-003", "项目明道立项", "明道立项", "manual", 1, "high"),
        ("W-004", "执行云资源安全基线扫描（自动化工具）", "现状调研", "auto", 2, "high"),
        ("W-005", "评审数据加密（静态/传输中）覆盖情况", "现状调研", "manual", 2, "high"),
        ("W-006", "评估当前账号整体安全评分", "现状调研", "manual", 2, "high"),
        ("W-007", "评估稳定性架构现状（单点/多AZ/备份策略）", "现状调研", "manual", 2, "high"),
        ("W-008", "评估成本使用现状（闲置/未优化资源识别）", "现状调研", "manual", 2, "med"),
        ("W-009", "评估效率管理现状（标签/资源组/账号体系）", "现状调研", "manual", 2, "med"),
        ("W-010", "评估性能现状（监控覆盖率/弹性配置）", "现状调研", "manual", 2, "med"),
        ("W-011", "安全模块方案设计（人员身份/程序身份/网络/数据安全）", "5模块方案", "manual", 4, "high"),
        ("W-012", "稳定模块方案设计（数据备份/监控管理/删除保护/多AZ）", "5模块方案", "manual", 4, "high"),
        ("W-013", "成本模块方案设计（付费方式优化/闲置资源/成本监控）", "5模块方案", "manual", 3, "med"),
        ("W-014", "效率模块方案设计（标签规范/默认资源组/账号体系优化）", "5模块方案", "manual", 3, "med"),
        ("W-015", "性能模块方案设计（性能监控/弹性伸缩/规格优化）", "5模块方案", "manual", 3, "med"),
        ("W-016", "《WA治理方案》三方评审与优化调整", "方案评审", "manual", 4, "high"),
        ("W-017", "安全模块实施（权限策略/网络安全组/加密配置）", "5模块实施", "manual", 8, "high"),
        ("W-018", "优化网络边界防护（WAF/IPS）配置", "5模块实施", "manual", 2, "high"),
        ("W-019", "稳定模块实施（备份策略/监控告警/删除保护）", "5模块实施", "manual", 6, "high"),
        ("W-020", "执行故障模拟演练（Chaos Engineering）", "5模块实施", "auto", 4, "med"),
        ("W-021", "优化备份恢复与灾备（DR）计划", "5模块实施", "manual", 4, "high"),
        ("W-022", "识别并清理闲置云资源", "5模块实施", "manual", 2, "med"),
        ("W-023", "评估预留实例（RI）/节省计划覆盖率", "5模块实施", "manual", 2, "med"),
        ("W-024", "优化资源规格匹配度（Right-sizing）", "5模块实施", "manual", 2, "med"),
        ("W-025", "效率模块实施（标签批量补全/资源组重组）", "5模块实施", "manual", 4, "med"),
        ("W-026", "性能模块实施（弹性伸缩策略/监控大盘配置）", "5模块实施", "manual", 4, "med"),
        ("W-027", "评审跨可用区（Multi-AZ）高可用架构", "5模块实施", "manual", 2, "high"),
        ("W-028", "《WA治理方案》终稿校对与确认", "交付收尾", "manual", 2, "high"),
        ("W-029", "《项目验收报告》编写", "交付收尾", "doc", 2, "high"),
        ("W-030", "交付邮件发送", "交付收尾", "manual", 1, "high"),
    ]},
}
# ---- 阶段出口门禁（每个阶段末一条 gate；判据缺失 → 待确认，不伪造）----
GATE_CRITERIA: dict[str, list[str]] = {
    "售前对接": ["客户需求与痛点已书面确认", "目标云/方案初步方向已对齐"],
    "明道立项": ["项目已立项（内部立项号已生成）", "项目经理与交付阵型已指定"],
    "信息调研": ["源端资产清单已回收并标准化", "应用依赖关系已确认"],
    "需求调研": ["账号体系/网络/权限/安全/财务/合规/运维 七项调研完成"],
    "现状调研": ["安全基线扫描已完成", "五模块现状评估结论已出"],
    "方案设计": ["HLD/LLD 已评审通过", "容量规划与选型已确认"],
    "5模块方案": ["五模块（安全/稳定/成本/效率/性能）方案已出"],
    "方案评审": ["方案三方评审通过并签字"],
    "HLD评审": ["LandingZone HLD 与 LLD 评审通过"],
    "POC验证": ["POC 环境已验证业务可用", "UAT 功能与数据一致性校验通过"],
    "实施部署": ["生产环境资源已就绪", "生产数据全量+增量同步完成", "业务联调验证通过"],
    "5模块实施": ["五模块改造项已实施完成", "故障演练与备份恢复已验证"],
    "IaC自动化": ["Terraform 模板已编写并通过流水线", "各账号配置一致性校验通过"],
    "工具部署": ["目标集群与组件已就绪", "迁移工具已部署并调通"],
    "数据迁移": ["存量数据与元数据迁移执行完成"],
    "数据校验": ["count/MD5/业务指标三级校验通过"],
    "双跑验证": ["源/目标双跑结果对比一致"],
    "割接上线": ["正式割接完成且业务全链路回归通过"],
    "交付收尾": ["测试资源已释放", "验收报告已客户确认", "交付邮件已发送"],
}
DEFAULT_GATE = ["阶段出口检查项「待确认」（本 skill 无该阶段事实判据，须现场补，不得臆造）"]

PRIO_CN = {"high": "高", "med": "中", "low": "低"}
TRIG_CN = {"manual": "人工", "auto": "自动/工具", "doc": "文档交付"}


class OrchError(Exception):
    pass


def load_track(name: str) -> dict:
    t = TRACKS.get((name or "").strip().lower())
    if not t:
        raise OrchError(f"未知 track: {name}（可选: {sorted(TRACKS)}）")
    return t


def build_actions(track: dict, extra: list[dict], scale: float) -> list[dict]:
    """展开 track 的 action 库 + 用户补充项，附阶段序号与缩放后工时。"""
    acts: list[dict] = []
    for (aid, name, phase, trig, hours, prio) in track["actions"]:
        acts.append({"id": aid, "name": name, "phase": phase, "trigger": trig,
                     "hours": round(hours * scale, 2), "hours_raw": hours,
                     "priority": prio, "source": "track"})
    for e in (extra or []):
        aid = (e.get("id") or "").strip()
        if not aid:
            raise OrchError("extra_actions 每项必须有 id")
        if any(a["id"] == aid for a in acts):
            raise OrchError(f"extra_actions id 与 track 内置重复: {aid}")
        ph = (e.get("phase") or "").strip()
        if ph not in GATE_CRITERIA and ph not in {a["phase"] for a in acts}:
            raise OrchError(f"extra_actions 未知 phase: {ph}")
        try:
            h = float(e.get("hours"))
        except (TypeError, ValueError):
            raise OrchError(f"extra_actions {aid} 缺合法 hours")
        acts.append({"id": aid, "name": (e.get("name") or aid).strip(),
                     "phase": ph, "trigger": (e.get("trigger") or "manual").strip(),
                     "hours": round(h * scale, 2), "hours_raw": h,
                     "priority": (e.get("priority") or "med").strip(),
                     "source": "extra", "depends_on": list(e.get("depends_on") or [])})
    return acts


def phases_of(track: dict, acts: list[dict]) -> list[str]:
    """阶段顺序：以 track 内置库的出现顺序为准，补充项的阶段追加到其宿主阶段之后。"""
    order: list[str] = []
    for a in acts:
        if a["phase"] not in order:
            order.append(a["phase"])
    return order


def build_deps(acts: list[dict], user_deps: dict) -> dict[str, list[str]]:
    """依赖：默认「同阶段内按序串接 + 跨阶段接上一阶段最后一项」。"""
    ids = [a["id"] for a in acts]
    idset = set(ids)
    for k in (user_deps or {}):
        if k not in idset:
            raise OrchError(f"depends_on 含未知 action id: {k}")
        for p in (user_deps[k] or []):
            if p not in idset:
                raise OrchError(f"depends_on[{k}] 含未知前置 id: {p}")
    deps: dict[str, list[str]] = {}
    prev_phase_last: str | None = None
    cur_phase: str | None = None
    prev_in_phase: str | None = None
    for a in acts:
        if a["phase"] != cur_phase:
            cur_phase = a["phase"]
            prev_in_phase = prev_phase_last
        d = list(a.get("depends_on") or [])
        if prev_in_phase and prev_in_phase not in d:
            d.append(prev_in_phase)
        for p in (user_deps or {}).get(a["id"], []):
            if p not in d:
                d.append(p)
        deps[a["id"]] = d
        prev_phase_last = a["id"]
        prev_in_phase = a["id"]
    return deps


def add_workdays(start: date, n: int) -> date:
    """从 start 起推进 n 个工作日（跳过周六周日）；n=0 返回 start 本身（若 start 是周末则顺延）。"""
    d = start
    step = 0
    while step < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            step += 1
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def schedule(acts: list[dict], deps: dict[str, list[str]], start: date | None,
             hpd: float, team: int) -> tuple[dict[str, dict], float]:
    """串行工时累加求 ES/EF；team>1 仅用于折算日历日（并行度粗估，不装精细调度）。"""
    byid = {a["id"]: a for a in acts}
    st: dict[str, dict] = {}
    total_h = 0.0
    for a in acts:
        ds = deps.get(a["id"], [])
        es_h = max((st[d]["ef_h"] for d in ds if d in st), default=0.0)
        ef_h = es_h + a["hours"]
        st[a["id"]] = {"es_h": es_h, "ef_h": ef_h, "hours": a["hours"]}
        total_h = max(total_h, ef_h)
    # 关键路径：沿 EF 最大者回溯
    cp: list[str] = []
    cur = max(st, key=lambda k: st[k]["ef_h"]) if st else None
    seen = set()
    while cur and cur not in seen:
        seen.add(cur)
        cp.append(cur)
        ds = deps.get(cur, [])
        cur = max(ds, key=lambda d: st[d]["ef_h"]) if ds else None
    cp.reverse()

    if start:
        # 日历日：按“工作日偏移”推进（跳过周六周日）；team 只影响每天可消耗的工时池
        h_per_day = max(hpd, 0.5) * max(team, 1)
        for a in acts:
            s = st[a["id"]]
            off_s = int(s["es_h"] // h_per_day)
            span = max(1, int(round(s["hours"] / h_per_day)))
            s["start_day"] = add_workdays(start, off_s)
            s["end_day"] = add_workdays(start, off_s + span)
    for a in acts:
        st[a["id"]]["critical"] = a["id"] in cp
    return st, total_h


def workdays_between(d1: date, d2: date) -> int:
    n = 0
    d = d1
    while d < d2:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def build(data: dict) -> dict:
    project = (data.get("project") or "").strip()
    if not project:
        raise OrchError("缺必填字段 project")
    track = load_track(data.get("track"))
    try:
        scale = float(data.get("scale", 1.0))
    except (TypeError, ValueError):
        raise OrchError("scale 必须是数字")
    if scale <= 0 or scale > 20:
        raise OrchError(f"scale 越界（0<scale<=20）: {scale}")

    acts = build_actions(track, data.get("extra_actions"), scale)
    phases = phases_of(track, acts)
    deps = build_deps(acts, data.get("depends_on") or {})

    done = set(data.get("done") or [])
    idset = {a["id"] for a in acts}
    unknown_done = sorted(done - idset)
    blocked_raw = data.get("blocked") or []
    blocked = {}
    for b in blocked_raw:
        bid = (b.get("id") if isinstance(b, dict) else str(b)).strip()
        if bid not in idset:
            raise OrchError(f"blocked 含未知 action id: {bid}")
        blocked[bid] = (b.get("reason") if isinstance(b, dict) else "") or "（原因未填，交付前须说明）"

    st, total_h = schedule(acts, deps, parse_date(data.get("start_date")),
                           float(data.get("hours_per_day") or 8), int(data.get("team_size") or 2))

    # 阶段汇总 + 门禁
    ph_summary = []
    for p in phases:
        sub = [a for a in acts if a["phase"] == p]
        ph_summary.append({
            "phase": p,
            "count": len(sub),
            "hours": round(sum(a["hours"] for a in sub), 2),
            "done": sum(1 for a in sub if a["id"] in done),
            "blocked": [a["id"] for a in sub if a["id"] in blocked],
            "gate": {"criteria": GATE_CRITERIA.get(p, DEFAULT_GATE),
                     "known": p in GATE_CRITERIA},
        })

    open_h = round(sum(a["hours"] for a in acts if a["id"] not in done), 2)
    done_h = round(sum(a["hours"] for a in acts if a["id"] in done), 2)
    pct = round(done_h / total_h * 100, 1) if total_h else 0.0

    start = parse_date(data.get("start_date"))
    cal = None
    if start:
        hpd = float(data.get("hours_per_day") or 8)
        team = max(int(data.get("team_size") or 2), 1)
        days_needed = total_h / (hpd * team)
        end = start
        added = 0
        while added < days_needed:
            if end.weekday() < 5:
                added += 1
            if added >= days_needed:
                break
            end += timedelta(days=1)
        cal = {"start": start.isoformat(), "end": end.isoformat(),
               "workdays": workdays_between(start, end) + 1,
               "assumption": f"{hpd:g}h/人日 × {team} 人并行（粗估，未考虑依赖排队与资源冲突）"}

    return {
        "project": project,
        "track": {"key": (data.get("track") or "").strip().lower(),
                  "cn": track["cn"], "prefix": track["prefix"]},
        "phases": ph_summary,
        "actions": [{"id": a["id"], "name": a["name"], "phase": a["phase"],
                     "trigger": a["trigger"], "hours": a["hours"],
                     "priority": a["priority"], "source": a["source"],
                     "depends_on": deps.get(a["id"], []),
                     "status": "blocked" if a["id"] in blocked else ("done" if a["id"] in done else "pending"),
                     "blocked_reason": blocked.get(a["id"]),
                     **({"start": st[a["id"]]["start_day"].isoformat(),
                         "end": st[a["id"]]["end_day"].isoformat()} if "start_day" in st[a["id"]] else {}),
                     "critical": st[a["id"]]["critical"]} for a in acts],
        "critical_path": [a["id"] for a in acts if st[a["id"]]["critical"]],
        "stats": {"total_actions": len(acts), "done": len(done & idset),
                  "blocked": len(blocked), "pending": len(idset - done - set(blocked)),
                  "total_hours": round(total_h, 2), "done_hours": done_h, "open_hours": open_h,
                  "pct": pct},
        "calendar": cal,
        "scale": scale,
        "unknown_done": unknown_done,
    }


def parse_date(v):
    if not v:
        return None
    s = str(v).strip()
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise OrchError(f"start_date 非法（须 YYYY-MM-DD）: {s}")


STATUS_CN = {"done": "✅完成", "blocked": "🚩阻塞", "pending": "⏳待办"}


def render_md(r: dict) -> str:
    L: list[str] = []
    s = r["stats"]
    t = r["track"]
    L.append(f"# 实施编排 · {r['project']}")
    L.append("")
    L.append(f"- 交付轨道：**{t['cn']}**（`{t['key']}`，Action 前缀 `{t['prefix']}`）")
    L.append(f"- Action 总数：**{s['total_actions']}** ｜ 阶段数：**{len(r['phases'])}**")
    L.append(f"- 总工时：**{s['total_hours']:g} h** ｜ 已完成 {s['done_hours']:g} h ｜ 剩余 {s['open_hours']:g} h ｜ 完成率 **{s['pct']:g}%**")
    L.append(f"- 状态分布：完成 {s['done']} ｜ 阻塞 {s['blocked']} ｜ 待办 {s['pending']}")
    if r.get("scale") and abs(r["scale"] - 1.0) > 1e-9:
        L.append(f"- 工时缩放系数 scale = **{r['scale']:g}**（相对基线工时放大/缩小）")
    if r["calendar"]:
        c = r["calendar"]
        L.append(f"- 日历：{c['start']} → {c['end']}（{c['workdays']} 个工作日，已跳过周末）")
        L.append(f"- 排期假设：{c['assumption']}")
    else:
        L.append("- 日历：未给 start_date，**不出日历日**（不编造日期）")
    L.append("")

    # ---- 阶段汇总 + 门禁 ----
    L.append("## 一、阶段汇总与出口门禁")
    L.append("")
    L.append("| # | 阶段 | Action 数 | 工时(h) | 已完成 | 阻塞 | 出口门禁判据 |")
    L.append("|---:|---|---:|---:|---:|---:|---|")
    for i, p in enumerate(r["phases"], 1):
        g = p["gate"]
        crit = "；".join(g["criteria"])
        if not g["known"]:
            crit = "⚠️ " + crit
        L.append(f"| {i} | {p['phase']} | {p['count']} | {p['hours']:g} | {p['done']} | "
                 f"{len(p['blocked'])} | {crit} |")
    L.append("")
    L.append("> ⚠️ 标阶段表示本 skill 无该阶段的事实判据，须现场补齐，**不得臆造**。")
    L.append("")

    # ---- 关键路径 ----
    L.append("## 二、关键路径")
    L.append("")
    cp = r["critical_path"]
    # 默认依赖为“同阶段串接”，此时关键路径必然是整条链；须显式声明避免误读为真实瓶颈
    fully_serial = len(cp) == r["stats"]["total_actions"]
    if fully_serial:
        L.append(f"未显式提供 `depends_on`，按**同阶段顺序串接**推演，关键路径覆盖**全部 {len(cp)} 项**。")
        L.append("")
        L.append("→ 真实并行度须由项目经理在 `depends_on` 中标注（可并行的项去掉前置依赖）后重算，")
        L.append("  否则本表只代表「最保守的串行下界」。")
    else:
        L.append(" → ".join(f"`{x}`" for x in cp) if cp else "（无）")
    L.append("")
    L.append("> 关键路径为工时累计最长的依赖链；任一节点延误即整体工期延误，须优先保障资源。")
    L.append("")

    # ---- 按阶段明细 ----
    L.append("## 三、Action 明细（按阶段）")
    L.append("")
    has_cal = any("start" in a for a in r["actions"])
    for p in r["phases"]:
        sub = [a for a in r["actions"] if a["phase"] == p["phase"]]
        L.append(f"### {p['phase']}（{len(sub)} 项 · {sum(a['hours'] for a in sub):g} h）")
        L.append("")
        head = "| ID | 任务 | 触发 | 工时(h) | 优先级 | 依赖 | 状态 |"
        sep = "|---|---|---|---:|:--:|---|---|"
        if has_cal:
            head = head[:-1] + " 起 | 止 | 关键 |"
            sep = sep[:-1] + "|---|---|:--:|"
        L.append(head)
        L.append(sep)
        for a in sub:
            dep = "、".join(f"`{d}`" for d in a["depends_on"]) or "—"
            row = (f"| `{a['id']}` | {a['name']} | {TRIG_CN.get(a['trigger'], a['trigger'])} | "
                   f"{a['hours']:g} | {PRIO_CN.get(a['priority'], a['priority'])} | {dep} | "
                   f"{STATUS_CN.get(a['status'], a['status'])} |")
            if has_cal:
                row += f" {a.get('start','—')} | {a.get('end','—')} | {'★' if a['critical'] else ''} |"
            L.append(row)
        L.append("")

    # ---- 阻塞清单 ----
    bl = [a for a in r["actions"] if a["status"] == "blocked"]
    L.append("## 四、🚩 阻塞清单")
    L.append("")
    if bl:
        L.append("| ID | 任务 | 阶段 | 阻塞原因 | 工时(h) |")
        L.append("|---|---|---|---|---:|")
        for a in bl:
            L.append(f"| `{a['id']}` | {a['name']} | {a['phase']} | {a.get('blocked_reason') or '—'} | {a['hours']:g} |")
    else:
        L.append("无阻塞项。")
    L.append("")

    # ---- 待确认 ----
    L.append("## 五、待确认项（不得臆造）")
    L.append("")
    n = 0
    for p in r["phases"]:
        if not p["gate"]["known"]:
            n += 1
            L.append(f"{n}. 阶段「{p['phase']}」缺出口门禁判据，须结合现场验收标准补齐。")
    if r.get("unknown_done"):
        n += 1
        L.append(f"{n}. `done` 中含非本 track 的 Action id（已忽略）：{', '.join(f'`{x}`' for x in r['unknown_done'])}。")
    done_no_fact = [a for a in r["actions"] if a["status"] == "blocked" and not a.get("blocked_reason")]
    if done_no_fact:
        n += 1
        L.append(f"{n}. 阻塞项未填原因：{', '.join(f'`{a["id"]}`' for a in done_no_fact)}。")
    if not n:
        L.append("无。")
    L.append("")

    # ---- 口径声明 ----
    L.append("## 六、口径声明")
    L.append("")
    L.append("- Action 库**全部来自客户执行计划看板真表**，本 skill 不臆造任务、不虚构进度。")
    L.append("- 本产物**只含工时（h）与工期（工作日）**，**不含任何费用或报价信息**；报价一律由 `pcs-quotation` 出具。")
    L.append("- 工时 ≠ 报价，亦不等于合同人月；转报价须先经 `pcs-quotation` 按职级费率与阵型折算。")
    L.append("- 日历仅在提供 `start_date` 时给出，且已跳过周末；未考虑法定节假日与资源冲突，须项目经理复核。")
    L.append("")
    return "\n".join(L)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="云迁移交付编排（阶段 04 实施）")
    ap.add_argument("--self-test", action="store_true", help="跑内置自检")
    ap.add_argument("--input", help="输入 JSON 路径")
    ap.add_argument("--out-dir", default=".", help="输出目录")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.input:
        print("用法: delivery_orch.py --self-test | --input x.json --out-dir DIR", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        r = build(data)
    except OrchError as e:
        print(f"[输入错误] {e}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as e:
        print(f"[输入错误] 读取/解析失败: {e}", file=sys.stderr)
        return 2
    md = render_md(r)
    assert_no_amount(md)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "delivery_orch.md").write_text(md, encoding="utf-8")
    (out / "delivery_orch.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {out/'delivery_orch.md'}")
    print(f"OK -> {out/'delivery_orch.json'}")
    print(f"stats: {json.dumps(r['stats'], ensure_ascii=False)}")
    return 0


def assert_no_amount(md: str) -> None:
    """红线自检：产物不得出现任何金额相关字样。"""
    for bad in ("¥", "￥", "月费", "单价", "人天", "总价", "元/"):
        if bad in md:
            raise OrchError(f"产物出现金额字样「{bad}」，违反零金额红线")


def self_test() -> int:
    ok = 0
    fail: list[str] = []

    groups: dict[str, list[bool]] = {}

    def chk(gid: str, name: str, cond: bool, extra: str = ""):
        groups.setdefault(gid, []).append(bool(cond))
        print(f"  {'OK ' if cond else 'FAIL'} {name} {extra if not cond else ''}")

    def errs(fn) -> str:
        try:
            fn()
            return ""
        except OrchError as e:
            return str(e)

    # ①② 四个 track 的 Action 数与阶段数必须等于看板真表
    want = {"business-migration": (46, 9), "landing-zone": (41, 8),
            "bigdata-migration": (34, 9), "well-architected": (30, 7)}
    for k, (na, nph) in want.items():
        r = build({"project": f"T-{k}", "track": k})
        gid = "①" if k == "business-migration" else "②"
        chk(gid, f"{key_cn(k)} 内置 {na} 条 / {nph} 阶段",
            r["stats"]["total_actions"] == na and len(r["phases"]) == nph,
            f"实得 {r['stats']['total_actions']}/{len(r['phases'])}")

    # ③ 内置 track 的阶段门禁全部有事实判据
    all_known = True
    for k in want:
        r = build({"project": f"T-{k}", "track": k})
        all_known = all_known and all(p["gate"]["known"] for p in r["phases"])
    chk("③", "③四个 track 全部阶段门禁判据 known=True", all_known)

    # ④ done 回填 → 状态/工时/完成率
    r = build({"project": "T-done", "track": "business-migration", "done": ["A-001", "A-002"]})
    a1 = next(a for a in r["actions"] if a["id"] == "A-001")
    a2 = next(a for a in r["actions"] if a["id"] == "A-002")
    exp_done = round(a1["hours"] + a2["hours"], 2)
    chk("④", "④done 回填：status=done 且 done_hours/pct 正确",
        a1["status"] == "done" and a2["status"] == "done"
        and abs(r["stats"]["done_hours"] - exp_done) < 0.01
        and abs(r["stats"]["pct"] - round(exp_done / r["stats"]["total_hours"] * 100, 1)) < 0.1)

    # ⑤ blocked：有 reason / 空 reason 落默认文案
    r = build({"project": "T-blk", "track": "business-migration",
               "blocked": [{"id": "A-035", "reason": "专线未开通"}, {"id": "A-036"}]})
    b35 = next(a for a in r["actions"] if a["id"] == "A-035")
    b36 = next(a for a in r["actions"] if a["id"] == "A-036")
    chk("⑤", "⑤blocked：status=blocked 且未填原因落默认文案",
        b35["status"] == "blocked" and b35["blocked_reason"] == "专线未开通"
        and b36["status"] == "blocked" and bool(b36["blocked_reason"]))

    # ⑥ 输入防线
    chk("⑥", "⑥未知 track 报错", bool(errs(lambda: build({"project": "x", "track": "no-such"}))))
    chk("⑥", "⑥未知 blocked id 报错",
        bool(errs(lambda: build({"project": "x", "track": "landing-zone", "blocked": [{"id": "Z-999"}]}))))
    chk("⑥", "⑥非法 start_date 报错",
        bool(errs(lambda: build({"project": "x", "track": "landing-zone", "start_date": "2026/11/03"}))))
    chk("⑥", "⑥scale=0 报错", bool(errs(lambda: build({"project": "x", "track": "landing-zone", "scale": 0}))))
    chk("⑥", "⑥scale=21 报错", bool(errs(lambda: build({"project": "x", "track": "landing-zone", "scale": 21}))))
    chk("⑥", "⑥缺 project 报错", bool(errs(lambda: build({"track": "landing-zone"}))))

    # ⑦ extra_actions
    r = build({"project": "T-extra", "track": "business-migration",
               "extra_actions": [{"id": "A-100", "name": "专线开通跟进", "phase": "实施部署",
                                  "trigger": "manual", "hours": 4, "priority": "high",
                                  "depends_on": ["A-034"]}]})
    a100 = next(a for a in r["actions"] if a["id"] == "A-100")
    chk("⑦", "⑦extra_actions 可加入且 phase/depends_on 生效",
        r["stats"]["total_actions"] == 47 and a100["phase"] == "实施部署"
        and "A-034" in a100["depends_on"])
    chk("⑦", "⑦extra_actions 重复 id 报错",
        bool(errs(lambda: build({"project": "x", "track": "business-migration",
                                 "extra_actions": [{"id": "A-001", "phase": "实施部署", "hours": 1}]}))))
    chk("⑦", "⑦extra_actions 未知 phase 报错",
        bool(errs(lambda: build({"project": "x", "track": "business-migration",
                                 "extra_actions": [{"id": "A-900", "phase": "不存在的阶段", "hours": 1}]}))))

    # ⑧ 有 start_date 时日历日必须跳过周末
    r = build({"project": "T-cal", "track": "business-migration",
               "start_date": "2026-11-03", "hours_per_day": 8, "team_size": 2})
    days = [(a["start"], a["end"]) for a in r["actions"]]
    chk("⑧", "⑧有 start_date：全部起止日均为工作日（跳周末）",
        all(date.fromisoformat(s).weekday() < 5 and date.fromisoformat(e).weekday() < 5
            for s, e in days) and r["calendar"] is not None)
    r2 = build({"project": "T-nocal", "track": "business-migration"})
    chk("⑧", "⑧无 start_date：不出日历日", r2["calendar"] is None
        and all("start" not in a for a in r2["actions"]))

    # ⑨ 关键路径
    chk("⑨", "⑨关键路径非空且起点 ES=0",
        len(r["critical_path"]) > 0
        and next(a for a in r["actions"] if a["id"] == r["critical_path"][0])
        ["depends_on"] == [])

    # ⑩ 零金额红线
    md = render_md(r)
    chk("⑩", "⑩md 零金额：无 ¥/月费/单价/人天",
        not any(b in md for b in ("¥", "￥", "月费", "单价", "人天")))

    # ⑪ 默认同阶段串接
    a2d = next(a for a in r["actions"] if a["id"] == "A-002")
    chk("⑪", "⑪默认依赖：同阶段按序串接（A-002 依赖 A-001）", a2d["depends_on"] == ["A-001"])

    for gid in sorted(groups):
        if all(groups[gid]):
            ok += 1
        else:
            fail.append(gid)
    print(f"\n自检: {ok}/11 通过" + (f"，失败组: {fail}" if fail else ""))
    return 0 if ok == 11 and not fail else 2


def key_cn(k: str) -> str:
    return TRACKS[k]["cn"]


if __name__ == "__main__":
    sys.exit(main())
