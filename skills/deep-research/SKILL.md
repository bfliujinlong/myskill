---
name: deep-research
description: Use when 深度研究某主题并出带引用报告. 四段流水线双模式.
version: 0.2.0
author: hermes
license: MIT
---

# Deep Research（对标 AWS Quick Research 的研究流水线）

> v0.2：已用真实 AWS Quick Research 样本（《国内外主要云厂商迁移上云方案调研报告》，77 来源/~8000字）校准。样本拆解见 `references/quick-research-sample-analysis.md`，样本原件存 `assets/`。

## When to Use

用户说「深度研究 X」「研究一下给我报告」「对比 X 和 Y 出报告」「deep research」时激活。普通一两个事实查询不触发（直接 web_search 回答）。

## 模式选择

| 模式 | 时长 | 适用 | 执行方式 | 篇幅基准 |
|---|---|---|---|---|
| **Fast** | 3-8 分钟 | 单一主题、事实核实、快速对比 | 主 agent 自跑 2-4 轮 web_search + web_extract | 1500-3000 字，10-20 来源 |
| **Deep** | 15-30 分钟 | 竞品拆解、选型报告、多子题并行 | delegate_task 并行子 agent + 圆桌交叉验证 | 6000-9000 字，50-80 来源 |

用户未指定时：子题 ≤2 用 Fast，>2 或要求「全面/深度」用 Deep。不确定就问一句。

## 流水线

### 1. Plan（研究计划）
- 拆成 3-6 个子问题，每个写明：需要什么证据、来源类型（官方文档/独立评测/新闻/论文/社区）
- **对象分层**（Quick 范式）：主要对象逐个深展开，次要对象合并成「概览」一节——研究资源不等分
- **统一维度框架**（Quick 范式）：所有对象用同一组分析维度（如迁移场景：应用工具/大数据工具/方法论），每个维度用 topic-sentence 段落（「应用迁移工具体系。……」），保证横向可比
- Deep 模式：计划先给用户确认再跑；Fast 直接跑
- 明确排除项

### 2. Gather（并行采集）
- 官方文档源优先（docs.*/help.*/learn.*/cloud.google.com 等），每子题至少 1 个官方源
- 中英文关键词各试；web_extract 抓正文，大页面落盘分段读
- **主动捕捉时效性变更**：产品停售/改名/新功能（如「Snow Family 停止新客户」「Migration Hub → AWS Transform」），标注「自 YYYY-MM-DD 起」
- **数据颗粒度**：抓具体数字/规格/容量/价格，不要「较快/较大」这类模糊词
- 抓不到 → 换源或 research/blocked-page-recovery；**不得凭标题脑补**
- Deep 模式：每子问题一个 delegate 子 agent，返回「结论 + 来源 URL + 关键引文」；中间结果落盘 scratch

### 3. Validate（验证与引用）
- **行内引用 [n] 制**（Quick 范式）：每个事实性断言句尾挂 [n]，多来源 [1, 2, 3]；表格单元格内也带引用；References 放末尾编号 URL 列表
- 关键数字 ≥1 可点击来源；冲突时并列标注
- 区分「官方宣称」vs「第三方独立评测」，官方自测打折标注
- 产品/价格类信息限近 6 个月来源
- 加载 research/grounded-citations 执行引用规范

### 4. Report（组装报告）

**Deep 模式默认用 Quick 咨询报告体**（样本已验证）：
```
# 标题（《……调研报告》）
## Executive Summary        ← 学术式三段：总判断→最关键发现→风险/注意点，内嵌引用
## 引言：背景与研究范围      ← 市场背景 + 范围界定 + 对象定位一句话画像
## 主要对象分节详述          ← 每对象一节，内部按统一维度 topic-sentence 展开
## 其他对象概览              ← 次要对象合并，每个 1-3 句 + 引用
## 跨对象对比                ← 大对比表（维度×对象，单元格带引用）+ 图表说明
## 专题深潜                  ← 合规/风险/最佳实践等横切议题，不局限于罗列产品
## 总结与选型建议            ← 场景化：什么画像的用户→选什么，逐条对应
## References                ← 编号 URL 平铺列表（不分类，编号与行内 [n] 对应）
```

**Fast 模式用速览体**（Telegram 聊天场景）：
```
# 标题
> 日期 · 来源说明
## 速览（3-5 核心结论，✅⚠️❌）
## 对比表
## 关键发现
## 建议动作（成本排序，零成本在前）
## 来源清单
```

通用规则：
- 写入 `/home/ubuntu/research/<主题>-<日期>.md`
- 交付：Telegram 发摘要 + `MEDIA:` 附件发全文；长报告必须发文件
- 用户要 docx 时用 ~/build_*.py 风格生成（黑灰禁蓝，模版无颜色无 AI 感）

## 红线
- 零成本优先：调研不产生付费调用；付费 API 实测前先确认免费层
- 不编造：来源不可达就明说；数字对不上重新核实
- 凭证不进报告、不进聊天
- 报告落盘文件是交付物本体，聊天摘要只是索引

## 零件映射

| 环节 | 工具 |
|---|---|
| 搜索 | web_search（中英双语） |
| 抓取 | web_extract / browser_exec（JS 页） |
| 并行子研究 | delegate_task |
| 交叉验证 | panel.py 圆桌（/home/ubuntu/panel4/，串行） |
| 引用规范 | research/grounded-citations |
| 发布 | MEDIA: Telegram / pubdoc 飞书+钉钉 |
