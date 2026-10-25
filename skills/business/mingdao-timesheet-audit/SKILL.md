---
name: mingdao-timesheet-audit
description: 明道云（mingdao.anchnet.com）工时确认单合理性核查。当需要检查工时填报是否合理、审计合作伙伴/员工工时、查看"记录-确认中"审批单、发现周末工时 / 0 小时记录 / 重复填报 / 周期错配 / 缺少工作内容时使用。覆盖登录、表格提取、规则核查、报告输出全流程。触发词：检查工时、工时核查、工时确认、工时审核、明道云工时、timesheet audit。
agent_created: true
---

# 明道云工时确认单核查

## 适用场景

- 项目经理（如刘金龙）收到「合作伙伴工时确认」「工时填报」审批单，需要判断能否点"同意"
- 需要核对周末 / 节假日工时、0 小时空记录、重复填报、周期错配
- 需要按人 / 按项目统计工时总量（人日）

## 前置条件

| 项 | 说明 |
|---|---|
| agent-browser | `npm install -g agent-browser`（已装则跳过）；浏览器在 `~/.agent-browser/browsers/chrome-*` |
| 登录方式 | 飞书扫码 + 授权（明道云无密码登录入口，走飞书 SSO） |
| Bash PATH | Git Bash 下需先 `export PATH="/usr/bin:/bin:$PATH"`，否则 `head/grep/seq` 不可用 |
| Python | `python3` |

## 工作流

### 步骤 1：登录（首次 / token 过期时）

```bash
export PATH="/usr/bin:/bin:$PATH"
agent-browser goto "https://mingdao.anchnet.com/app/<目标URL>"
# 1) 若跳到 /network?ReturnUrl=... → 未登录
agent-browser snapshot | grep -E "link|button"     # 找 link "飞书登录" [ref=eN]
agent-browser click eN                              # → 跳 accounts.feishu.cn
# 2) 用户用飞书 App 扫码
agent-browser screenshot                            # 存到 ~/.agent-browser/tmp/screenshots/
cp <最新截图> <工作区>.png                           # 复制出来用 present_files 给用户扫
# 3) 扫码后进入"飞书授权"页（title=飞书授权）
agent-browser snapshot | grep button                # 找 button "授权" [ref=eN]
agent-browser click eN
# 4) 回调停在 /auth/feishu?... 时不会自动跳，手动 goto 目标 URL
agent-browser goto "https://mingdao.anchnet.com/app/<目标URL>"
agent-browser get title                             # 应显示单据标题，如「记录-确认中」
```

⚠️ 二维码约 2 分钟过期，超时需 `agent-browser reload` 重新截图。
⚠️ `agent-browser open` 首次可能阻塞，用后台执行 + 后续 goto 即可。

### 步骤 2：提取表格数据

明道云工作表**无 `<table>`**，单元格是 `div.editableCellCon`，class 内含 `row-N` / `col-M`。

```bash
# 提取当前页（每页约 25-30 行）
agent-browser eval "var cells=[...document.querySelectorAll('div[class*=editableCellCon]')]; var rows={}; cells.forEach(function(c){var m=c.className.match(/row-(\d+)/); var cm=c.className.match(/col-(\d+)/); if(!m||!cm)return; (rows[m[1]]=rows[m[1]]||{})[cm[1]]=c.textContent.trim();}); JSON.stringify(rows)" > page1.json

# 翻页
agent-browser eval "var i=[...document.querySelectorAll('.pagination .icon-arrow-right-border')].pop(); i.click(); 'clicked'"
# 重复上面 eval 存 page2.json ...
```

典型列顺序（以「合作伙伴工时确认」为例）：
`1=确认状态 2=姓名 3=填报日期 4=日期状态 5=人员参与项目 6=项目名称 7=工时`

⚠️ eval 的 stdout 是 **JSON 字符串**（需 `json.loads` 两次）。
⚠️ `--output-path` 不是 `eval` 参数，必须用 shell 重定向 `> file.json`。

### 步骤 3：合并 + 规则核查

```bash
python3 scripts/audit_timesheet.py page1.json page2.json -o report.md
```

脚本输出：按人/项目汇总、问题清单、工作日覆盖缺口。

### 步骤 4：输出报告

按「结论先行 → 待确认明细 → 问题表 → 已排除疑点 → 建议」结构输出。
可选：导出 Excel 留档（openpyxl）。

## 审核规则

| # | 规则 | 判定 | 严重度 |
|---|---|---|---|
| R1 | 周末 / 节假日实报工时 | 日期状态=周末 且 工时>0 | ❌ 高 |
| R2 | 调休上班日被误判 | 周日/周六 但属国务院调休上班日 → **放行**，见 `references/holiday_2026.md` | ✅ 排除 |
| R3 | 0 小时空记录进入确认 | 工时=0 且 状态=确认中 | ❌ 高 |
| R4 | 已退回记录混入新确认单 | 同一单据内状态既有「退回」又有「确认中」 | ❌ 高（同意时可能连退回行一起放行） |
| R5 | 周期错配 | 单据标题"周度确认"但数据跨度 > 2 周 | ⚠️ 中 |
| R6 | 缺少工作内容列 | 表只有项目+日期+工时，无任务描述 | ⚠️ 中（无法核验） |
| R7 | 工时颗粒度单一 | 确认中记录 ≥90% 为整 8h，无差异 | ⚠️ 低-中 |
| R8 | 同一人同日多项目 | 合计 > 8h → 超报；= 8h → 需确认拆分合理 | ⚠️ 中 |
| R9 | 工作日覆盖缺口 | 该人区间内工作日无记录（可能请假/漏报） | ⚠️ 需对照考勤 |
| R10 | 工时不满额 | 单日 < 8h 且无其他同日记录 | ℹ️ 提示 |

## 已知坑

1. **Bash PATH**：Git Bash 下 `dirname/head/seq` 找不到，必须 `export PATH="/usr/bin:/bin:$PATH"` 前置。
2. **PowerShell 工具不回显 stdout** —— 用 Bash 而不是 PowerShell 执行命令。
3. **虚拟滚动非无限滚动**：`.scroll-viewport` 滚动不会加载更多行，必须用 `.pagination .icon-arrow-right-border` 翻页。
4. **授权后不自动跳转**：飞书授权回调停在 `/auth/feishu?...&code=...`，需手动 `goto` 目标 URL。
5. **日期状态字段由系统判定**，但周日调休上班日可能被标"工作日"——不要直接判为异常，先查当年放假安排。
6. **审批按钮**：页面有 暂存 / 同意 / 拒绝 / 转审 / 加签 —— **未经用户明确指令不要点击**。

## 输出模板

```
整体：<总工时>h = <人日> 人日，<N> 人 × <M> 项目

【待确认明细】人员 | 项目 | 工时 | 天数 | 覆盖区间
【不合理 / 风险点】# | 问题 | 明细 | 建议
【核查后排除】疑点 → 结论
【需留意】工作日缺口 / 不满额
```

## 资源

- `scripts/audit_timesheet.py` — 合并分页 JSON + 规则核查 + 生成报告
- `references/holiday_2026.md` — 2026 年放假调休安排（判定 R2 用）
