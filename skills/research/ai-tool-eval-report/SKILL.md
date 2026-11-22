---
name: ai-tool-eval-report
description: "Use when 研究某 AI 工具/产品能力并对比同类工具做选型报告. 两轮联网核实+固定结构报告+零成本建议."
version: 2026-11-21.001
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [工具评估, deep-research, 选型报告, 竞品对比]
    related_skills: [cloud-price-bench, model-discovery, grounded-citations]
---

# AI 工具研究评估报告

## When to Use

触发：用户问「X 工具有个 Y 能力 / 哪个工具有类似能力 / 研究一下给我份报告」这类 AI 产品/工具调研选型请求。产出 = 研究对比报告（md 落盘）+ Telegram `MEDIA:` 附件 + 聊天内结论先行的速览摘要。不适用：云资源比价用 cloud-price-bench，免费模型探测用 model-discovery，客户交付咨询报告用 consulting-report-forge。

## 流程

1. **第一轮并行 web_search（3–4 组，中英混合）**：
   - 官方产品页/文档（能力拆解、工作流、模式与时限数字）
   - 定价与免费档（pricing / free plan / 注册门槛 / region）
   - 同类工具对比与独立基准（comparison、benchmark、arXiv 评测论文）
2. **第二轮定向核实（按第一轮缺口补查）**：
   - 免费档以**官方 FAQ 为准**逐条确认：要不要信用卡、要不要云厂商账号、试用期、区域可用性——定价页营销文案不算数
   - 开源替代：GitHub/HuggingFace 模型与 agent 框架、OpenRouter/DashScope 上的 API 可用性、外部依赖 key（搜索/网页读取服务的免费额度）
3. **报告落盘** `/home/ubuntu/research/<主题>-对比报告-<日期>.md`，用下面固定结构。
4. **交付**：`MEDIA:` 发文件附件；聊天内只给速览（结论第一句、表格、✅⚠️❌），结尾用一个问句给下一步选项，不长篇复述报告。

## 报告固定结构（用户偏好）

1. 目标产品能力拆解：工作流表格 + 差异化卖点；数字必须来自官方文档
2. 定价表：**$0 通道单独强调**（零成本红线：是否要卡、是否要云账号、注册入口）
3. 同类工具全景，**三分法**各一张表：海外商业 / 国内商业 / 开源自部署——开源自部署是一等公民（零成本 + 数据不出本机）
4. 独立基准排名表（arXiv 论文出处），并与厂商宣称对照
5. **对照用户已有栈**：Hermes 零件（web_search/web_extract/delegate_task/panel 圆桌/grounded-citations/pubdoc/百炼账号）逐项映射目标产品能力，给出「零件已有 X 成、缺的是 Y」式结论
6. 对安畅业务的关联：售前交付物机会、AICCP/平台对标价值
7. 建议动作：立即做 / 短期做，全部 $0 优先
8. 来源清单附录（官方文档、论文、仓库分列）

## 红线与坑

- 厂商自称基准第一（「在 XX Bench 上最准」）必须找独立第三方论文印证；找不到就在报告中明确标注「仅官方自测，无独立评测」——营销宣称与独立评测的排名常不一致。
- 功能、定价、区域可用性一律以本次检索结果为准，不凭记忆断言；检索不足就继续检索或明确写不确定。
- 中文社区来源（知乎/公众号）只作观点线索，事实结论以官方文档与论文为准。
