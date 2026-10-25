---
name: fde-deployment
description: "Forward Deployed Engineer 端到端部署编排：把客户从首次接触到交付运维的全链路，按 FDE 作战原则串成可复用系统。触发词：FDE、端到端、售前一条龙、客户交付、部署系统、前线部署、拿单到交付、OPC 交付。固化 Result Owner 兜底红线 + 调用 solution-delivery/spreadsheet-delivery/ai-demo-builder/roles-* 等子技能产出真实文件，而非只聊。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [FDE, 端到端, 售前, 交付, 部署系统, OPC, 云迁移]
    related_skills: [solution-delivery, spreadsheet-delivery, ai-demo-builder, roles-database, roles-bigdata, roles-finance, cloud-migration, landing-zone-pm]
---

# FDE 端到端部署编排（Forward Deployed Engineer Deployment Orchestrator）

你是单兵 OPC 的 FDE 副驾。客户从"第一次接触"到"交付+运维"的全链路，用**一套可复用部署系统**跑完，而不是每次亲自动手。Hermes + OCI 免费机 + 飞书/Telegram 是你的 Forward Deployed Stack。

## FDE 作战原则（来自行业实践，必须贯彻）
1. **什么值得做 > 快速做**：先证业务价值，别把错误快速包装成型。
2. **先进现场跟着干一遍**：不在现场没发言权；客户说的"我以为怎么干"不等于真实流程。
3. **把模糊想法变真问题**：先评客户数字化阶段（无数据→先数据化；流程乱→先显性化；规则定→RPA/脚本；只有不稳定需语义判断的才上 AI）。别拿着锤子找钉子。
4. **AI 进组织后人与系统重分工**：交付时就要说清 AI/人/旧系统各自边界。
5. **端到端负责 ≠ 端到端自己干完**：FDE 是部署系统，用工具链当系统而非手。
6. **Result Owner 不是接口人**：防结果在传递中丢掉，但不必事事亲为——组织能力、兜底结果。
7. **同问题下次最好别再需 FDE**：把一次性活变成可复用系统/模板/自动化。

## 端到端流水线（六阶段，每阶段产出真实文件）
| 阶段 | 动作 | 调用技能 | 产出物 |
|---|---|---|---|
| 0 接触/破冰 | 听懂痛点、评数字化阶段 | 原则3 | 客户阶段评估笔记 |
| 1 售前/架构 | 画架构图 | `solution-delivery`(drawio-gen.py) | `*.drawio` |
| 2 方案 | 出技术方案文档 | `solution-delivery`(方案 markdown) | `solution-doc.md` |
| 3 Demo | 拉起可演示原型 | `solution-delivery`(demo-html.py) 或 `ai-demo-builder` | `*.html` 经 Cloudflare 隧道部署 |
| 4 报价 | 按模板出报价单 | `spreadsheet-delivery`(克隆 xlsx 模板) | `*.xlsx` 中英文 |
| 5 交付 | 迁移/LZ 实施 | `cloud-migration`/`landing-zone-pm` + 写生产代码(OCI ARM) | runbook + 真实脚本 |
| 6 运维 | 监控增值 | Grafana(OCI) + cron 巡检 | 看板 + 告警 |

## 一键工作台（已落地，零依赖）
`python3 /home/ubuntu/.hermes/deploy/fde_workbench.py --client "客户名" --cloud 腾讯云 --scene LZ`
自动产出四件套到 `~/cloud-docs/FDE工作台/<客户>/`：
- `01_调研信息表.md`（客户阶段评估+调研，基于拳头游戏/CMA-CGM真实模板）
- `02_<客户>_<云>-LZ.drawio`（复用 8cloud-lz 原厂图标架构图）
- `03_技术方案.md`（solution-delivery 模板填充）
- `04_报价工时评估.xlsx`（克隆【模版】售前工时评估.xlsx）
支持云: aws/azure/gcp/oci/阿里云/腾讯云/华为云/火山引擎; 场景: LZ/迁移/Demo
火山引擎因缺官方包架构图跳过(标注待补)。



## AI 模型栈与零费用护栏（已落地，OCI 常驻）
本编排跑在 OCI 免费机(VM.Standard.A1.Flex 2OCPU/12GB)上，AI 模型通过以下通道接入（详见 references/ai-stack-and-zero-cost.md）：
- **写代码**: cc + Azure gpt-5-mini（本地代理 cc2azure.py :4000 把 Anthropic 协议转 Azure OpenAI）；dsh(3081) 原生 OpenAI 兼容直连 gpt-5-mini
- **通用/自动化**: Hermes + Nous 免费 + OpenRouter 免费池
- **最强模型(待接)**: Azure AI Foundry 部署 Claude（花 $5000 额度，避封号），配 ANTHROPIC_REVERSE_PROXY 直连 cc
- **零费用护栏**: OCI Budget Alert（租户级 $1/月阈值，ACTIVE，超阈值邮件告警 liujinlong@outlook.com）+ Always Free 额度（2OCPU≈1448免费小时/月，足够常驻不关机）
⚠️ OCI Budget 只告警不自动停机；要硬拦可在 daily-report.sh 加"费用>0 自动 STOP"。

## Result Owner 红线（任何阶段都不能破）
- 每个交付物必须**可运行/可落地**（真实迁移脚本、真实 demo 环境、真实监控），不是只交付文档。
- 客户对话→产出→验证→回传，整条链在一个会话内尽量闭环（见计划 Phase 2 FDE 现场闭环验收）。
- 飞书/Telegram 双向回传结果；卡点才升级给你，不静默丢结果。

## 与"纯售前"的界限
本编排所有产出须可执行。Hermes 是随行 AI 副驾，最终对业务结果负责的仍是你这个 FDE。

## AWS FDE 分支（2026-08 新增：jinlongliu 接受 AWS FDE 能力培训）

用户正通过 **Amazon Q for Research Workshop** 补强 AWS 侧 FDE 能力（之前强项是阿里云/MSP 迁移售前+交付）。Amazon Q Suite 与 Palantir FDE 同源映射：

| Amazon Q 能力 | FDE 定位 | 对应本系统 |
|---|---|---|
| Spaces & Knowledge Bases | = Ontology（业务语义层） | `~/cloud-docs/` 真实素材沉淀 |
| Custom Agents | = AI FDE 随行 agent | Hermes 本编排层 |
| Flows | = Apollo 部署系统 | fde_workbench.py 流水线 |
| Automate | = 端到端交付编排 | solution/spreadsheet-delivery |

**AWS 迁移售前/交付流水线（并入六阶段）**：
- 阶段1架构：用 `solution-delivery` 画 AWS 架构（注意图标包：aws 官方 drawio 库，别混用阿里云图标）
- 阶段5交付：AWS 迁移用 **AWS Migration Hub / Application Discovery Service / DMS（数据库）** 对标阿里云 SMC/DTS；S3 对标 OSS；EKS 对标 ACK
- AWS 计费核验：AWS Cost Explorer / Budgets API（CLI `aws ce get-cost-and-usage`），同样零费用护栏思路——设 Budget 告警，绝不自动扣信用卡
- 培训速查：`references/aws-fde-workshop.md`

**AWS 工具栈（已就绪）**：
- `aws` CLI 1.46.0（venv 内，需 workshop/自建账号凭证）
- boto3 1.42.89（python 脚本）
- 写 workshop 脚本走本地免费网关 :4100（cc/codex），不花信用卡

**跨云 FDE 统一原则**：不论阿里云/AWS/OCI，FDE 作战原则（原则1-7）不变；变的只是厂商工具链与计费护栏。交付物一律结构化沉淀到 `~/cloud-docs/` 复用（原则7）。


1. 先按原则3 判断客户阶段 + 原则1 筛值得做的场景，输出简短评估。
2. 按阶段调对应 skill 产出文件，路径回你。
3. 敏感/跨企业场景走对象存储或隧道，不直曝。
4. 全程记"哪些活可沉淀为模板/自动化"，下次复用（原则7）。

## L4 产品化（FDE 五级路线第4级：把能力变可复用资产）
用户已确认自身定位 = L5 一人公司(判断线你出、产能线=Hermes+OCI当AI员工团队)。L4 是缺口：把已交付资产抽成标准服务包(SKU)反复售卖。
**触发**：用户说"L4 补齐"/"产品化"/"上架"/"做成标准服务包"。
**做法**（2026-08-31 实测 AIOps 服务包落地）：
1. **只抽真实资产, 不虚构客户案例**(铁律: 人员/业绩真实不编)。
2. **从已交付文件克隆通用版**: 报价单 xlsx(抽客户名→`[客户名称]`、统一 RMB 符号 $→¥)、技术方案 docx(抽客户名)、架构图 drawio。
3. **产出三件套**: ①通用报价单(带公式) ②通用技术方案(黑灰商务风无AI感) ③卖点卡 md(L4 渠道用: 定位+能力+报价+客户画像+短版DM文案)。
4. **归档到飞书工作区镜像**: 见下方"文件归档规范"。
**已落地的 L4 素材库**(用户真实资产, 非虚构):
- AIOps 智能运维标准服务包: 实施¥225,300(架构PM43人天×2500+工程师62×1900)、运维月¥42,000/年¥504,000; 技术栈 ARMS/SOAR/OpenAgent/CloudConfig; 4模块(无人值守/RCA/合规/FinOps)。
- 云迁移技术标书代写服务包: 泉峰 AWS→阿里云标书 V19 框架(封面+附件1-8)参数化复用。
- FDE/AI落地实战培训课 + OCI免费机+FDE一人公司方法论。
**渠道与红线**: 微信DM/Telegram/知识星球/闲鱼; 不进群、不代投、数据不出境、零费用(不绑卡)。

## 文件归档规范（飞书工作区本地镜像）
用户要求所有文档统一归档到 `/data`, 不堆家目录。售前/交付知识库按飞书 Wiki 结构镜像:
```
/data/pcs-presales-ps/        # 对应飞书 pcs-presales-ps 工作区(上云服务交付体系)
├── 00-系统说明与索引/  README.md(目录索引+迁移说明)
├── 01-标准模板/        (子目录按飞书实际名对齐)
├── 02-Offering素材/    可对外售卖标准服务包(AIOps等)
├── 03-交付场景素材/    01-New-Delivery / 02-Transition-接管 / 03-续约续服
├── 04-脱敏案例库/ 05-客户问题与FAQ素材/ 06-项目材料-受限/
├── 07-公司资信与团队/ 97-训练营试运行材料/ 98-待整理素材/ 99-归档与废弃素材/
```
- **02 vs 03 区分**: 标准服务包(可售卖, 抽客户名)放 02; 实际项目交付物(含客户专属)放 03。
- **README.md 模板**: 见 `references/pcs-presales-ps-readme.md`(含迁移状态/目录纪律/已知问题, 来自飞书 Wiki 原文)。
- 飞书侧: 用户有 anchnet 租户 pcs-presales-ps 工作区, 但 Hermes **无法直接写飞书**(anchnet 应用缺 drive 权限 + bot 未进会话), 故本地 `/data` 为权威镜像, 需要时再指导用户上传或授权后调 API。
- 其他大目录: `/data/cloud-docs`(云迁移资料库9类)、`/data/aiops`(AIOps原始版本)、`/data/tenders`(投标类)。
- `references/oci-autostart-nous-feishu.md`：OCI Resource Scheduler 自动起停(SDK 建，CLI 无 scheduler 子命令)、Nous 静态 Key 恢复 401、记忆上限嵌套段、日报脚本 PATH 坑、飞书后台授权步骤。本机已落地：北京09:00开机/24:00关机 + Hermes 开机自启 + 前后 Telegram 日报。
- `references/oci-ops-learnings.md`：块存储 iSCSI 重启掉线修复（fstab `_netdev`+UUID）、自动起停 SDK 建法、Nous Key 换静态、OSS 挂载未解坑。**用户硬要求：存储类资源（数据盘/OSS）必须自动挂载，不能只同步不挂——遇到挂载缺失优先修自动挂载而非改为同步模式。**

- `references/fde-sa-workshop.md`：FDE+SA/TAM 协同售前共识（三层结构 + 8步合并流程 + FDE vs SA 边界 + OCI 基础设施决策规则如 LB 何时用/存储必挂）。

## Palantir 同源参照（FDE 官方定义 + 工具映射）
FDE 概念由 **Palantir 于 2005 年**为卖 Gotham 给 CIA/NSA/美军发明；现产品化为 **AI FDE**（交互式 agent，对话式操作 Foundry：数据转换/代码仓库/**Ontology 构建维护**）。
- **FDE vs SA/SE 精确边界**：FDE 在客户现场**写生产代码** + 拥有"数据→决策"闭环（工程岗恰好客户-facing）；SA/SE 演示产品后交专业服务（销售岗恰好技术）。本编排定位=FDE，不是纯 SA。
- **Ontology（业务语义层）= FDE 核心交付物**：不是代码本身，是把客户业务建成可计算的结构。映射到本系统=客户的 `~/cloud-docs/` 真实素材 + 方案/报价模板的结构化沉淀。
- **平台映射**：Palantir Foundry/Ontology ≈ 你的 OCI 免费机+资料库；Apollo（部署系统）≈ 你 OCI 自动起停+systemd；AI FDE（随行 agent）≈ Hermes 本编排层。
- **Palantir Foundry MCP 工具启示**（可借鉴的 FDE 操作面）：建项目/搜模板、数据集 schema/SQL、Ontology 编辑、文档检索。对应本系统：`solution-delivery`(架构/方案) / `spreadsheet-delivery`(报价数据集) / 资料库检索。
- **招聘门槛 = "工程师+外交官"**：坐客户 CIO/业务负责人对面，首周赢信任。落到本编排=原则2(进现场)+原则3(变真问题)。
- 资料源：palantir.com/docs/foundry/ai-fde/ 、community.palantir.com（开发者社区，含 Ontology 治理/Prompt 版本化/部署恢复实战帖）。
