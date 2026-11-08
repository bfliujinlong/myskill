---
name: migration-team
description: "端到端云迁移交付团队编排：七阶段（方案→计划→执行→实现→交付→验收→收尾）统一编排，PM 为 Result Owner 持有 state.json，按阶段调度 6 个角色 agent（架构师/工程师/数据库/大数据/安全/财务）。触发词：组队、team、端到端、全流程、项目编排、迁移团队、从方案到验收、交付流水线。"
version: 0.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [端到端, team, 编排, PM, 云迁移, 交付]
    related_skills: [pm-agent, roles-architect, roles-engineer, roles-database, roles-bigdata, roles-security, roles-finance, cloud-migration, landing-zone-pm, solution-delivery, spreadsheet-delivery]
---

# 端到端交付团队编排（七阶段）

单兵 OPC 的虚拟交付团队。**PM 是 Result Owner**，持有项目唯一真相源，按阶段调度专业角色。
不是并发起一堆 agent 各干各的——是**一条有门禁的流水线**：前一阶段出口没过，下一阶段不开工。

## 团队名册

| 角色 | 技能 | 主责阶段 | 输出物 |
|---|---|---|---|
| **PM**（Result Owner） | `pm-agent` | 全部 7 阶段 | state.json、周报、验收报告、复盘 |
| 架构师 | `roles-architect` / `migration-architect` | 方案、交付 | 6R 评估、目标架构、SLA 分档 |
| 财务 | `roles-finance` / `finance-ops` | 计划、收尾 | 报价单、TCO、回款台账 |
| 工程师 | `roles-engineer` / `migration-engineer` | 执行、实现 | Terraform/ROS、迁移脚本、runbook |
| 数据库工程师 | `roles-database` | 执行、实现 | schema 转换、DTS 方案、性能校验 |
| 大数据工程师 | `roles-bigdata` | 执行、实现 | 数据迁移、ETL、数仓管道 |
| 安全工程师 | `roles-security` | 实现、验收 | IAM 基线、密钥审计、合规检查 |

## 七阶段流水线（阶段 → 主责 → 出口门禁）

```
0 方案 solution   架构师     → 方案文档 + 架构图；客户认可范围
1 计划 plan       PM+财务    → WBS + 报价单 + SOW；SOW 签署
2 执行 execute    工程师系列  → IaC + 迁移脚本 + runbook；里程碑交付物到位
3 实现 implement  工程师+安全 → 环境就绪 + 安全评审通过；验收测试用例跑通
4 交付 deliver    PM+架构师  → 交付包 + 培训记录；客户签收单
5 验收 accept     PM+客户    → 验收报告 + 遗留问题清单；客户签字
6 收尾 close      PM+财务    → 复盘 + 回款记录；款项到账 + 资产归档
```

**门禁纪律**：出口不满足不得推进；P0 风险未关闭该阶段不得标 done。

## 状态机 CLI（PM 的真相源，非手写 JSON）

```bash
PY=/home/ubuntu/.hermes/hermes-install/venv/bin/python3
S=/home/ubuntu/.hermes/scripts/pmstate.py

$PY $S init <项目> --cloud 阿里云 --type 迁移
$PY $S show <项目>              # 看当前阶段/关卡/风险/里程碑
$PY $S artifact <项目> <阶段> <文件路径>
$PY $S risk <项目> add --level P0 --desc "..." --owner XX --due 2026-11-05
$PY $S ms <项目> add --id M1 --name "LZ落地" --due 2026-11-10
$PY $S next <项目>              # 卡点检查：能否推进下一阶段
$PY $S set <项目> <阶段> done   # 推进（自动把下一阶段置 in_progress）
$PY $S report <项目>            # 生成进展汇报
```

状态文件：`~/cloud-docs/pm/<项目>/state.json`

## 调度模式

### 模式 A：单角色深做（默认，省 token）
只对当前阶段主责角色派 `delegate_task`，PM 串行推进。适合多数项目。

### 模式 B：阶段内并行（执行/实现阶段）
执行阶段可并行派工程师 + 数据库 + 大数据，各自交付到 `~/cloud-docs/delivery/<项目>/<角色>/`，
由 PM 收口登记 artifact。注意：并行子 agent **无钉钉 MCP**，文档走 `docsync`（见 `agent-doc-access`）。

### 派活 context 必带四件套
1. 项目名 + 当前阶段 + 项目背景（源云/目标云/规模）
2. 已抓取到本地的文档路径（`~/cloud-docs/_inbox/*.md`）
3. 本阶段要产出的**具体文件**及落盘路径
4. 引用对应 role skill 名，让它加载

## 收口检查（每阶段）

PM 在标 `done` 前必须确认：
- [ ] 交付物**文件真实存在**（用 terminal `ls` 验，不信 agent 自述）
- [ ] 无 P0 未关闭风险
- [ ] `pmstate next` 返回可推进

## 知识库管理与自动化同步

### 知识库结构

- **团队知识库**：每个团队拥有独立的知识库，存放 MCP 和 Skill，位于 `/home/ubuntu/.hermes/skills/{team_name}/`。
- **自学习知识库**：每个团队拥有自学习知识库，位于 `/home/ubuntu/.hermes/learning/{team_name}/`，用于记录学习日志和资源。
- **共享知识库**：公司通用规范、模板、报价单等文档存放于 `/home/ubuntu/cloud-docs/`。

### 自动化同步机制

1. **每日自动拉取更新**：使用 `sync_skills_to_learning.py` 脚本，每日自动拉取阿里 Skill Center 和腾讯 Skill Hub 的更新，并同步到各个团队的自学习知识库。

   ```bash
   0 9 * * * /home/ubuntu/.hermes/hermes-install/venv/bin/python3 /home/ubuntu/sync_skills_to_learning.py >> /home/ubuntu/.hermes/logs/skills_sync.log 2>&1
   ```

2. **学习日志记录**：每个团队成员每日提交学习日志，记录从 Skill Hub 拉取的 MCP/Skill 和资源，以及知识共享和下周计划。

   日志模板：
   ```markdown
   ---
   date: {date}
   team: {team_name}
   agent_id: hermes-agent-001
   ---
   ### 学习内容
   1. **阿里 Skill Center**
   - MCP: 
   - 新增: 
   - 更新: 
   
   2. **腾讯 Skill Hub**
   - 应用模板: 
   - 新增: 
   - 视频教程: 
   
   3. **GitHub**
   - 开源项目: 
   - 学习: 
   
   ### 知识共享
   - 
   
   ### 下周计划
   - 
   ```

### 知识库同步脚本

脚本 `sync_skills_to_learning.py` 实现自动同步功能，确保知识库保持最新状态。

```python
# 示例脚本片段
import os
import json
import requests
from datetime import datetime

def create_daily_log(team_name):
    log_dir = os.path.join(f"/home/ubuntu/.hermes/learning/{team_name}", "daily_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.md")
    with open(log_file, 'w') as f:
        f.write("""---
date: {date}
team: {team_name}
agent_id: hermes-agent-001
---
### 学习内容
1. **阿里 Skill Center**
   - MCP: 
   - 新增: 
   - 更新: 

2. **腾讯 Skill Hub**
   - 应用模板: 
   - 新增: 
   - 视频教程: 

3. **GitHub**
   - 开源项目: 
   - 学习: 

### 知识共享
- 

### 下周计划
- 
""".format(date=datetime.now().strftime('%Y-%m-%d'), team_name=team_name))
```

PM 在标 `done` 前必须确认：
- [ ] 交付物**文件真实存在**（用 terminal `ls` 验，不信 agent 自述）
- [ ] 无 P0 未关闭风险
- [ ] `pmstate next` 返回可推进

子 agent 自述"已完成"不等于完成——父 agent 必须自己验文件存在。

## 父 agent 验货三查（2026-10-27 实战，必做）

子 agent 回传后父 agent 亲自跑，**不要只看 summary**：

1. **查文件真实存在**：`ls -la` + `wc -c`。只看 summary 会漏（子 agent 曾自述 WBS 9 项，父 `head -40` 只看到 8 项，实际 W9 在后面；中英双版导致 grep 计数翻倍，需去重再核）。
2. **查数字自洽**：金额与人天用脚本重算校验，别信文本里的"合计"。实测 `350 × 183 = 64,050` 一次通过。
3. **查时间线冲突**：把 P0 风险 due 与里程碑 due 排序比对。实测抓到两处真实冲突：
   - R2 数据驻留合规 11-07 **早于** M1 LZ落地 11-10 → 合规未批先建 LZ（中东 Fintech 硬伤）
   - R3 异构 DDL 兼容 11-14 **晚于** W5 数据库迁移开工 11-12 → 未验证先施工

**P0 风险 due 必须早于其阻塞的里程碑/任务开工日**，这是排期自检的核心规则。

## 空状态不等于没风险
阶段显示"零交付物、零风险"往往是**状态机没被填充**，不是项目真没风险。
PM 首次进入某阶段时，`next` 绿灯不代表可以推进——先确认该阶段是否已被真实动作填充过。

## 文档接入
子 agent 工具箱无钉钉 MCP，飞书也常拿不全。统一用 `agent-doc-access` 技能：
父 agent 先 `docsync` 拉成本地 md，把路径塞进 context，子 agent 直接读文件。

## 红线
- 不编造进度/人员/案例；缺素材写"未核实"
- 零费用：不因编排产生任何付费调用
- 交付物落 `~/cloud-docs/delivery/<项目>/`，收尾阶段归档到 `/data`
