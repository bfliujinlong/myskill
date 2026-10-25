# Work 技能区索引（与 personal/ 物理隔离）

本文件是 work 类技能的逻辑归类索引。work 类 skill 仍留在 `skills/` 根目录（含用户自有 skill：solution-delivery / spreadsheet-delivery，移动需 `hermes curator adopt`，此处不擅动）。

## 工作类技能（按业务线）

### 售前 / 方案
- `presales-architect` — 售前架构师：方案设计、RFP 应答、选型报价
- `solution-delivery` — 方案交付：架构图(drawio)/Demo/方案文档 【用户自有】
- `spreadsheet-delivery` — 表格交付：报价单/xlsx 克隆模板 【用户自有】
- `ai-demo-builder` — AI 演示方案工厂

### 云迁移 / 运维
- `cloud-migration` — 迁移评估/6R/割接
- `cloud-migration-pm` — 迁移项目管理
- `landing-zone-pm` — LZ 项目管理
- `multi-cloud` — 多云管理
- `oci-*` — OCI 免费机运维（oci-free-tier / oci-always-free-ops / oci-free-monitoring）
- `oci-always-free-ops` / `oci-free-tier` / `oci-free-monitoring`

### FDE 作战
- `fde-deployment` — 端到端部署编排（售前→交付→运维）

### 商务
- `business-development` — 商务拓展/谈判
- `sales` — 销售话术/漏斗
- `project-manager` — 项目管理
- `finance-ops` — 报价测算/TCO

### 模型 / 工程
- `model-router` — 免费多模型路由
- `overseas-model-hub` — 海外免费模型清单
- `roles-*` — 数据库/大数据/财务工程师
- `document-library-ingest` — 批量文档入库

### 平台 / 工具
- `weixin-voice` — 微信语音（注：微信无原生语音，实际走 Telegram）
- `hermes-agent` / `hermes-config-*` / `hermes-env-backup`

## 边界约定
- 用户说「客户/方案/报价/迁移/FDE/商务/云」→ 走本 work 区
- 用户说「个人/生活/健康/家人/收藏」→ 走 `skills/personal/` 区，不加载本区

## 2026-09-06 WorkBuddy 导入（WorkBuddy Agent 经 SSH 同步）
- `workbuddy-rules` — 全局公约+四细则（AC-MIG 定价 / SOW 14 章 / 去AI味 / 输出风格）
- `qy-dubaifintech-bid` — QY-DubaiFintech 报价项目档案（me-east-1，76EC2/27DB/45Redis/51TB，2AZ 双活）
- `aiccp-platform` — AICCP 平台架构与开发规范（三层架构 / AI 四段式）
- 文档处理六件套：`pdf` / `docx` / `xlsx` / `pptx` / `humanizer` / `summarize`
