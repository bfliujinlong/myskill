# 考试参数核实清单 + 已核实参数库

## 核实清单（每张认证都跑一遍）

| 项 | 从哪拿 | 为什么必须查 |
|----|--------|------------|
| 题数（计分 / 不计分） | exam guide PDF | 不计分题混在题中，影响答题节奏策略 |
| 时长 | exam guide / 认证页 | 定模拟卷限时（建议按 90% 时长练） |
| 通过线与分制区间 | exam guide | 反推模拟卷达标百分比 |
| 题型集合 | exam guide 的 Question types 段 | 决定模拟卷是否要出多选/排序/匹配/案例 |
| 域权重 | exam guide 的 Content outline | 驱动计划天数与题数分配 |
| 考试形式 | 认证页 Testing options | 在线监考需额外准备（系统要求/房间） |
| 语言 | 认证页 Languages offered | 中文译题术语偶尔生硬，需给用户选择建议 |
| 门市价 | 认证页 Cost | 标注券/优惠省下多少；付费模考另列 |
| In-Scope 服务清单 | exam guide 附表 | 模拟卷只考清单内服务，避免出超纲题 |
| 退役/改版公告 | 认证页顶部 notice | 语言或版本退役日期会改变考试窗口 |

**改版陷阱**：认证页与 exam guide 可能不同版（页已更新、PDF 仍是旧版）。两者对不上时以 **exam guide 的 Revisions 段**为准，并在计划里注明版本。

## 已核实参数库

### AWS Certified AI Practitioner (AIF-C01)
核实于 2026-10，来源 aws.amazon.com/certification/certified-ai-practitioner + 官方 exam guide PDF。

- 类别 Foundational；90 分钟；65 题（50 计分 + 15 不计分）
- 题型：单选 / 多选（5+ 选项选 2+）/ 排序（3–5 项）/ 匹配（3–7 对）/ 案例（一场景多问，逐问计分）
- 不计分题不标识，不答=错，**猜满不扣分**
- 分制 100–1000，通过线 **700**，pass/fail 制
- 门市价 $100；Pearson VUE 考场 或 OnVU 在线监考
- 语言含简体中文（意大利语/德语 2026-10-15 后退役）
- 定位：目标考生「有 ≤6 个月 AWS AI/ML 接触经验，使用但不构建 AI/ML 方案」→ 不考写代码、不考数学推导

域权重（计分内容占比 → 50 题模拟卷分配）：

| 域 | 内容 | 权重 | 50题卷 |
|----|------|------|-------|
| D1 | Fundamentals of AI and ML | 20% | 10 |
| D2 | Fundamentals of GenAI | 24% | 12 |
| D3 | Applications of Foundation Models | 28% | 14 |
| D4 | Guidelines for Responsible AI | 14% | 7 |
| D5 | Security, Compliance, and Governance for AI Solutions | 14% | 7 |

免费资源路径：Skill Builder 内官方 Learning Plan（免费数字课）→ Official Practice Question Set（免费题组）→ Practice Pretest（免费摸底）；Official Practice Exam 付费 $20（非必须）；Cloud Quest: Generative AI / AWS Jam 补服务边界。

高频混淆对（AIF-C01 出题重灾区）：

- **Bedrock vs SageMaker AI**：调用第三方/自研 FM + 统一 API + 托管 RAG/护栏/定制 = Bedrock；训练自有模型、超参控制、全栈基础设施 = SageMaker AI。题眼出现「训练/微调自有模型 + 自有基础设施」→ SageMaker。
- **JumpStart 定位**：开源模型一键部署/微调，介于 Bedrock 与全手工之间。
- **fine-tuning vs continued pre-training**：改「怎么说」（风格/格式，知识不变）→ fine-tune；改「知道什么」（灌领域语料，标签少）→ continued pre-training。
- **Knowledge Bases / Agents / Guardrails / Model Evaluation / Provisioned Throughput**：托管 RAG+引用 / 规划+工具调用（Action Group 挂 API，OpenAPI schema 定义）/ 内容过滤+拒答主题+PII+提示攻击检测 / 自动打分+人评队列 / 吞吐 SLA 预留。
- **Q Business vs Q Developer vs Bedrock**：企业知识助手 / 写代码 / 模型运行时。
- **Guardrails vs Rekognition**：前者管与模型交互的**文本**，后者管 UGC **图像/视频**违规检测。
- **Translate**：保留品牌词 = custom terminology；提升翻译质量 = parallel data。
- **SageMaker 推理四式**：常在线 = endpoint；突发间歇小模型 = Serverless；离线大批量 = Batch Transform；超大图片视频准实时 = Async。
- **隐私题固定答案**：Bedrock 客户内容不用于训练 FM 提供商模型；传输 TLS、静态默认加密，可换客户托管 KMS CMK；不出 VPC 用 bedrock-runtime 接口端点。
- **漂移**：线上效果衰退 → data/concept drift → SageMaker Model Monitor 告警。
- **可解释性**：SageMaker Clarify（特征重要性/SHAP）；**模型卡**：Bedrock 控制台可查各 FM 的用途/训练数据概况/局限。

### 其他认证（用户路线图，参数待各自核实）

用户既定路线：AWS AI Practitioner (AIF-C01) → AWS AI Engineer Associate → Azure AI-102，辅以阿里云 PAI / 华为 HCIA-AI。**未核实的参数一律不写进交付物**，按上方清单现查现填，查完补进本库。

## 兑换券时限规则（通用）

- 多数厂商券有**两层时限**：兑换窗口（收到后 N 天内「使用」）+ Use-By 日期。N 常见 30 天。
- 「使用/Used」的定义写在券的 Terms & Conditions 里，**通常是完成考试报名，不是完成考试**。读不准就按最严格解释（报名）执行。
- 未在兑换窗口内报名：券可被发行方**回收、作废、不再通知**。
- 报名后考试日期可以晚于报名日（在 Use-By 内即可）；改期/取消通常有免费窗口（考前 24h 以上），券随新日期保留。
- 券条款常含「发行方与考试赞助方可查看兑换状态与你取得的认证」——不同意就别兑换，这点要向用户点明。
- 退订提醒邮件的链接在 Pearson VUE 类系统里是独立的，与报名无关。
