# AWS FDE 培训速查（Amazon Q for Research Workshop）

## Workshop 入口
https://catalog.us-east-1.prod.workshops.aws/event/dashboard/en-US/workshop
主题：Amazon Quick Suite（Spaces/知识库、Custom Agents、Flows、Automate）
时长：~2.5h 动手（Intro 10 + Setup 15 + Intelligent Teammates 90）

## Amazon Q Suite 四件套（FDE 视角映射）
| Q 能力 | 干什么 | FDE 对应（Palantir 同源） |
|---|---|---|
| Spaces & Knowledge Bases | 领域知识库，连你的文献/资料 | = Ontology（业务语义层），FDE 核心交付物 |
| Custom Agents | 领域专家 agent，用你的上下文答问 | = AI FDE 随行 agent（Hermes 本编排层） |
| Flows | 自动化工作流，输入→结构化输出 | = Apollo 部署系统（可复用流水线） |
| Automate | 深度研究/多源综合报告 | = 端到端交付编排（本 fde-deployment） |

## 四个 Intelligent Teammates
1. Domain Expert（领域专家）
2. Research Assistant（研究助理）
3. Data Analyst（数据分析）
4. Automation Engineer（自动化工程师）
→ 对应 FDE 原则：把一次性活变成可复用系统（原则7）、人与系统重分工（原则4）

## 本机配套（已就绪，零费用）
- AWS CLI 1.46.0：venv 内 `aws`（需你 workshop 账号凭证才连 AWS）
- boto3 1.42.89：python 脚本调 AWS API
- 免费模型网关 :4100 / :4100 litellm：给 cc/codex 写 workshop 脚本用，不花信用卡
- OCI 免费机常驻：Hermes + dsh，交付物存 ~/cloud-docs/

## 注意
- workshop 自带头账号（活动提供）或自建 AWS 账号——**别用 OCI 的 Azure 额度/信用卡**
- Amazon Q 配置沉淀后可存成本机 skill 复用（见 fde-deployment AWS 分支）
