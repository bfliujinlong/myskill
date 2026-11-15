---
name: cloud-migration
description: "云迁移：评估、6R策略、迁移计划、割接与回滚、成本与风险管控。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [云迁移, 上云, 搬迁, 割接, 6R, migration]
    related_skills: [project-manager, presales-architect, multi-cloud, alibabacloud-migration-survey, migration-plan-gen]
---

# 云迁移（Cloud Migration）

## When to Use（何时使用）

## 调研评估上游（alibabacloud-migration-survey）

迁云评估阶段优先用 `alibabacloud-migration-survey` 产出结构化调研报告：已扩展为**源所有云（AWS/Azure/GCP/华为云/腾讯云/百度云/IDC）→ 目标所有云（含阿里云/OCI 等）**双向评估，输出客户画像、架构现状、云产品映射、版本兼容性风险、迁移风险与待确认事项。该报告是后续 6R 策略、迁移计划与报价测算的入口交付物（报告本身不报价、不实际迁移）。

- 客户要从 IDC/友商云迁移到目标云（如阿里云/华为云/AWS/GCP）
- 需要做迁移评估、制定 6R 策略、排迁移计划
- 涉及割接窗口、回滚预案、数据一致性校验
- 迁移后成本对比、优化建议

## 标准工作流

### 1. 知识库同步与团队结构
- **知识库同步**：
  - 使用 `sync_skills_to_learning.py` 脚本每日自动同步阿里云和腾讯 Skill Hub 的更新到各团队知识库。
  - 目录结构：
    ```
    /home/ubuntu/.hermes/learning/{team_name}/skills/
    /home/ubuntu/.hermes/learning/{team_name}/daily_logs/
    ```
  - 脚本：
    ```python
    #!/usr/bin/env python3
    import os
    import json
    from datetime import datetime
    
    def create_daily_log(team_name, learning_content):
        log_dir = os.path.join(f"/home/ubuntu/.hermes/learning/{team_name}", "daily_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.md")
        with open(log_file, 'w') as f:
            f.write(f"---
date: {datetime.now().strftime('%Y-%m-%d')}
team: {team_name}
---
{learning_content}")
    
    def sync_skills_to_learning(skills_data, team_name):
        skills_dir = os.path.join(f"/home/ubuntu/.hermes/learning/{team_name}", "skills")
        os.makedirs(skills_dir, exist_ok=True)
        for skill in skills_data:
            skill_file = os.path.join(skills_dir, f"{skill['name']}.json")
            with open(skill_file, 'w') as f:
                json.dump(skill, f, indent=2, ensure_ascii=False)
    
    # 示例调用
    teams = ['ceo', 'finops', 'compliance', 'ops', 'presales', 'migration-architect', 'aiops', 'devops', 'ops-monitoring', 'data', 'junior-dev', 'delivery']
    skills_data = [{"name": "bailian-cli", "status": "updated"}]
    for team in teams:
        sync_skills_to_learning(skills_data, team)
        create_daily_log(team, "学习内容...")
    ```

- **团队结构**：
  - 12 个团队，每个团队对应特定技术领域（AIOps、FinOps、大数据迁移等）和角色（售前、架构师、运维等）。
  - 知识库体系：Hermes + Obsidian，支持自主学习、知识积累和跨域协作。

### 2. 风险分析与预留
- **风险预留**：
  - 将风险预留从 13 人日提高到 **30–35 人日**，或改为“风险预留按实际发生另计”。
  - 风险登记表：
    - 识别技术陷阱、成本超支风险、角色定义模糊点。
    - 补充《首期范围确认单》以明确交付物范围。
    - 设独立里程碑以应对 ServiceNow 联调和 AgentCore 交付时间点的不确定性。

### 3. 现状盘点（发现）
- **资源清单**：
  - 计算、存储、网络、数据库、中间件、依赖的第三方服务
  - 耦合关系、量级、合规要求（等保/数据出境）

### 4. 6R 策略定级
| 策略 | 含义 | 适用 |
|------|------|------|
| Rehost 重新托管 | 直接搬（lift-shift） | 紧急上云、标准化应用 |
| Replatform 平台重构 | 小改适配托管服务 | 想减负运维 |
| Refactor 重构 | 云原生改造 | 长期成本/弹性诉求 |
| Repurchase 替换 | 换 SaaS | 非核心系统 |
| Retain 保留 | 暂不移 | 合规/依赖未清 |
| Retire 退役 | 下线 | 僵尸系统 |

### 5. 迁移计划模板
- 分批：先非核心→核心；先只读→读写
- 每批：评估→改造→演练→割接→观察
- 割接窗口：选低峰，明确起止、负责人、通讯群
- 回滚：数据快照/镜像前置，5 分钟内可回退

### 6. 割接检查清单
- [ ] 全量+增量数据同步完成，差异<阈值
- [ ] 一致性校验脚本通过
- [ ] DNS/网关切换预案就绪
- [ ] 旧环境保留可回滚（不立即销毁）
- [ ] 监控告警覆盖新环境
- [ ] 业务方验收口径一致

### 7. 成本对比
迁移前后 TCO：一次性（迁移人天）+ 月度（资源+流量+运维）对比，量化上云收益。

### 1. 现状盘点（发现）
- 资源清单：计算/存储/网络/数据库/中间件/依赖的第三方服务
- 耦合关系：调用链、数据流向、强依赖
- 量级：数据量、QPS、峰值、合规要求（等保/数据出境）
- 工具：各云都提供迁移中心/ATF（应用迁移服务）

### 2. 6R 策略定级
| 策略 | 含义 | 适用 |
|------|------|------|
| Rehost 重新托管 | 直接搬（lift-shift） | 紧急上云、标准化应用 |
| Replatform 平台重构 | 小改适配托管服务 | 想减负运维 |
| Refactor 重构 | 云原生改造 | 长期成本/弹性诉求 |
| Repurchase 替换 | 换 SaaS | 非核心系统 |
| Retain 保留 | 暂不移 | 合规/依赖未清 |
| Retire 退役 | 下线 | 僵尸系统 |

### 3. 迁移计划模板
- 分批：先非核心→核心；先只读→读写
- 每批：评估→改造→演练→割接→观察
- 割接窗口：选低峰，明确起止、负责人、通讯群
- 回滚：数据快照/镜像前置，5 分钟内可回退

### 4. 割接检查清单
- [ ] 全量+增量数据同步完成，差异<阈值
- [ ] 一致性校验脚本通过
- [ ] DNS/网关切换预案就绪
- [ ] 旧环境保留可回滚（不立即销毁）
- [ ] 监控告警覆盖新环境
- [ ] 业务方验收口径一致

### 5. 成本对比
迁移前后 TCO：一次性（迁移人天）+ 月度（资源+流量+运维）对比，量化上云收益。

## 6. 数据一致性双跑验证评审（交付物审查，高频）

迁移双跑/灰度期，客户或团队会产出"双跑验证计划与数据测试报告"类 xlsx（分层：ODS/DW/DM/SR/Hive核心/分区/推送任务/不可双跑等）。**这类表本质是结果登记的 tracker，常常名实不符、开口项未闭环**——作为 FDE 要把它审成可交付物。审查步骤：

1. **全覆盖**：用 openpyxl 逐 sheet 读，对每个状态列（名称可能为 验证状态/状态/结论/是否一致/割接上线状态/对象级校验状态/复核）做 `collections.Counter` 分布统计。一眼看出通过/未通过/无需割接占比。
2. **开口项（open items）闭环检查**：筛出「责任人 且 是否已修复 同时为空」的行——尤其当 失败字段数 高或 最低/平均一致率<90% 时，这是真风险。底稿里常占绝大多数（实测某 208 行 sheet 有 193 行开口、93 行低一致率且无人认领）。
3. **总览 vs 明细 叙事缺口**：总览判"通过"但明细有"不通过/不通过(复核:不用处理)"——要在报告正文用一句话统一解释为什么明细不通过仍算总体通过。
4. **白名单审计**：不一致行若全非白名单（既没加白也没填原因/修复），属未决，必须单列。
5. **真开口风险上提**：不可双跑/推送任务里 任务未通过 / 未上线（库表名变化等）节点，别被"已上线"多数淹没，单独拎出跟踪清单。
6. **格式健康度**：日期格式（20260807 / 2026-08-07 / 2026.08.04 混用）、状态词十余种、表尾 `None` 占位列——统一后才能交客户。

**升级成交付物三件事**（可让 Hermes 自动做）：① 补"报告正文"三页（范围/方法论/总体结论与遗留风险）；② 从 xlsx 自动抽"闭环清单"（已修复/可接受附理由/仍开口附责任人+计划日）；③ 清洗格式。

### 直接可跑的 openpyxl 审计脚本

```python
import openpyxl, collections
PATH = "/tmp/shuangpao.xlsx"  # 换成实际文件
wb = openpyxl.load_workbook(PATH, data_only=True)
STATUS_NAMES = ["验证状态","状态","结论","是否一致","割接上线状态",
                "对象级校验状态","复核"]
def col_index(hdr, name_part):
    for i,h in enumerate(hdr):
        if h and name_part in str(h): return i
    return None
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2: continue
    hdr = rows[0]
    print(f"\n=== {ws.title} ({len(rows)-1} 数据行) ===")
    for name in STATUS_NAMES:
        ci = col_index(hdr, name)
        if ci is None: continue
        cnt = collections.Counter(
            ("" if r[ci] is None else str(r[ci])) for r in rows[1:])
        print(f"  [{name}] {cnt.most_common(12)}")

# 开口项检测（适用"导入sr-非核心"类 sheet）
ws = wb["导入sr-非核心"]  # 换成实际 sheet 名
rows = list(ws.iter_rows(values_only=True)); hdr = rows[0]
cm = {h:i for i,h in enumerate(hdr) if h}
src, fail = cm["源表"], cm["失败字段数"]
minc, avg = cm["最低一致率"], cm["平均一致率"]
owner, fixed = cm["责任人"], cm["是否已修复"]
blank = low_no_owner = 0
for r in rows[1:]:
    o, fx = r[owner], r[fixed]
    if (o is None or str(o).strip()=="") and (fx is None or str(fx).strip()==""):
        blank += 1
    try: avn = float(r[avg]) if r[avg] not in (None,"") else 100
    except: avn = 100
    if avn < 90 and (o is None or str(o).strip()==""):
        low_no_owner += 1
print(f"\n开口项(责任人+是否已修复同空): {blank}, 均一致率<90%无人认领: {low_no_owner}")
```

## 常见陷阱
- 只搬主机不搬依赖，割接后连环故障
- 数据增量没算清，割接丢数据
- 旧环境割完立刻销毁，回滚无门
- 低估跨云网络成本（出网流量/专线）
- 双跑报告只登记不结论：开口项无人认领、总览判通过但明细不通过未解释、低一致率表淹没在"已上线"多数里

## 报价单交付格式（安畅 Excel 模板）

最终报价/人天交付物**默认用 Excel（安畅 PS 报价模板），不是 Word**。客户是外企时文档正文/会议用英文；报价 Excel 模板版式固定。

### 最终交付件格式映射（按用户确认口径）
- **人天评估** = `51D0E267` 双 sheet 模板（云迁移报价单 + 评估人天逻辑）：见下方「模板（固定版式）」。
- **报价评估** = 旺旺 `旺旺_AWS迁移_PS报价单_安畅.xlsx` 单 sheet 黑灰无蓝版式（列：`序号|产品名称/工作流|角色|数量人日|税率|单价|小计|备注`）。
- **IaC 单独报价** = 旺旺 单 sheet 同版式，仅含 WS3 包，金额与主报价包 C 严格守恒不重复计列。
- 三份独立 Excel；方案建议提案用 Word（外企英文交付，SOW §3.2）。
- 实施脚本样例（AIA 项目）：`/home/ubuntu/客户项目/AIA_云迁移/build_aia_xlsx.py`（51 双 sheet → 人天评估）、`build_aia_wangwang_xlsx.py`（旺旺单 sheet → 报价评估 + IaC）。

### 模板（固定版式，勿改结构）
- 人天评估模板：`/tmp/51D0E267-D2D0-44E2-9E10-01DCA671A74C.xlsx`（双 sheet：`云迁移报价单` + `评估人天逻辑`）。
- 报价评估 / IaC 模板：`/home/ubuntu/客户项目/旺旺/04_商务与合同/01_报价与测算/旺旺_AWS迁移_PS报价单_安畅.xlsx`（单 sheet，黑灰无蓝）。
- 实施脚本样例（AIA 项目）：`/home/ubuntu/客户项目/AIA_云迁移/build_aia_xlsx.py`（clone 模板 → 填表头锚点 + 明细行 + 重算逻辑页 → `soffice --headless` 重算公式落盘）。
- 字体：微软雅黑；小节标题填充 `FFF2F2F2`；金额格式 `\¥#,##0.00`；税率 `0%`；配色黑灰无蓝。

### 表头锚点（合并单元格必须写左上锚点，勿写非锚点格）
- 客户名称 `D5`；供应商 `D7`；客户经理名 `G7`/电话 `I7`/邮件 `I8`；架构师名 `G9`/电话 `I9`/邮件 `I10`。
- 客户联系人/电话/邮件（锚点 `E5`/`I5`/`I6`）填"待确认"，**勿把安畅的联系方式当客户联系方式**。
- 付款周期 `K7`=一次性；货币 `K9`=人民币；日期 `K5`=`=TODAY()`；有效期 `K6`=30天。
- 明细区 `B15:I18`（序号/产品名称/产品详情/数量/税率/单价G/小计I/备注K）；`B19`=不含税、`B20`=含税。

### 税公式方向（易错，严重）
- 模板默认假设**列 I 小计是含税**，自带 `G19=G20/1.06`、`G20=SUM(I15:J18)`。
- 若 rate card 单价是**不含税**（AIA 即此情况：架构师/PM ¥2,500、工程师 ¥1,900、税 6%），必须**反转公式**：
  `G19`(不含税)=`SUM(I15:I18)`，`G20`(含税)=`G19*1.06`，列 I 保持 `=E*G`（不含税行小计）。
- 出文件前用 `soffice --headless --convert-to xlsx` 重算，断言 `G19`/`G20` 与守恒脚本一致。

### Rate card 冲突处理
- 模板示例单价 ¥3,300 是别的项目基数，**不套用**；以本项目已验证 rate card 为准，并在「特别说明」标注冲突点。
- 模板示例人天（415.5/192.5/67.6）是别的项目基数，用本项目实测人天。**绝不在 docx/xlsx 虚构人员或案例**（废标风险）。

### 守恒纪律（落盘前必跑）
- 不含税总额 == Σ(人日×单价) == `pricing_result.json`；总人日 == 各行 quantity 之和。
- Package 小计之和 == 角色小计之和 == 总额；IaC 单独报价文档金额 == 主报价对应 Package，独立文档但**不重复计列**。
- 独立 verify 闸门（如 `verify_aia_pricing.py`，`errors:[]` 才出报价）。报价标注 `PREVIEW` 不批价。

### IaC 单独报价
- 单独 xlsx，金额 = 主报价对应 WS3 包（如 AIA：架构师 60×¥2,500 + 工程师 180×¥1,900 = 不含税 ¥492,000 / 含税 ¥521,520）。
- 风险预留（共享）只计在主报价，IaC 文件不重复计列，仅在特别说明引用。
