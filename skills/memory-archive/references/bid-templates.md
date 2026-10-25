云迁移资料库 ~/cloud-docs/ 9类104份(报价单/方案/LZ等). 报价单按SmartCare/Fintech模板1:1产中英文docx. 做方案优先引用对应文件夹真实素材.

---

用户以售前架构师身份为云迁移项目产出正式投标/技术标文档（docx），投标主体多为阿里云MSP（安畅网络科技模板 AC-SOW01-SM-230517 常被复用）。技术标标准8项结构：封面+附件1-8＝人员团队(迁移+运维双表)/类似业绩(迁移+运维各≥3个,2025-01-01后)/技术响应情况(响应S-01~S-04调研事项)/项目实施方案(含G0-G7里程碑周计划)/专业服务方案/增值服务说明/偏离表(技术,不接受负偏离)/声明及文件。

---

投标类任务铁律: 人员姓名/证书、类似业绩案例+合同证明等真实素材用户会给, AI绝不虚构(造假=废标+诚信黑名单)。用户明确'素材你不用管'指不要我编, 只更新格式/结构。改技术标要'格式统一'到用户指定的源框架文件(如V19), 不另起炉灶。

---

技术标偏离表更新经验(2026-08-26): V19偏离表是docx表18(四列:序号/招标要求/实报内容/偏离说明, 含备注4条+公章区+日期__2026__年__08__月__24__日)。用python-docx定位tbl、清空数据行(add_row填新行)即可扩展, 封面/业绩页不动。已扩到28行锚定SOW/招标条款号, 2正偏离+24无偏离+2部分偏离。SLA须分档写准(勿笼统99.9%), S-01/VPN须声明'非割接回退手段'。

---

Hermes skills已软链到Claude Code与Codex(单一真源, 绝对路径): ~/.hermes/skills/<cat>/<name> → ~/.claude/skills/<name> 与 ~/.codex/skills/<name>. 2026-08-27批量建79+个业务相关skill软链(售前/FDE/云迁移/投标/工程方法论/GitHub/运维/文档生成), 排除creative/apple/personal等噪音. cc/codex自动发现SKILL.md. 改Hermes skill后cc/codex自动同步. 验证: test -f ~/.codex/skills/<name>/SKILL.md.

---

AIOps 售前材料已交付(2026-08-29): 基于用户AIOPS.docx (4模块: 7x24无人值守/智能根因RCA/合规治理/FinOps, 阿里云技术栈ARMS/SOAR/ActionTrail/OpenAgent/CloudConfig)。克隆中东迪拜云迁移报价模板(中英文V2)生成 AIOps智能运维服务报价单(一次性$25k/月$16k/年$192k), 技术方案docx(黑灰商务风无AI感), 架构图drawio。关键校准: OpenAgent=阿里云云治理中心(Agentic CGC)编排中枢, CIS扫描/漂移检测由配置审计Cloud Config执行, 二者配套非同一产品。文件在 /home/ubuntu/AIOps*.*。

---

AIOps智能运维项目(基于AIOPS.docx, 阿里云技术栈ARMS/SOAR/OpenAgent/ActionTrail/Cloud Config): 已产技术方案docx+中英文报价单xlsx(克隆中东迪拜模板)+架构图drawio. 报价: 实施¥225,300(架构PM 2500×43人天+工程师1900×62人天), 运维月¥42,000/年¥504,000. OpenAgent定位=阿里云云治理中心(Agentic CGC)编排中枢, CIS扫描/漂移检测实际由Cloud Config执行(已校准方案描述). 英文报价单已将USD/$符号改RMB/¥.

---

用户正在构建售前资料库（SmartCare案例集），路径 /home/ubuntu/cloud-docs/SmartCare案例集/（北区/东1组/东2组）。后续会按方向（Landing Zone/云迁移/WA优化/大数据/DR/IaC等）要求抽取对应案例，整理成售前可用素材。已建 HLD 架构设计 Skill（~/.hermes/skills/business/hld-design.md）和售前报价 Skill。

---

【2026-09-06】项目台账：①QY-DubaiFintech：AWS→阿里云 me-east-1(迪拜)，76 EC2/27 DB/45 Redis/51TB/5源区，目标2AZ双活，报价冲刺中；②汤臣倍健 DataWorks 0621：Trino→Spark双跑，754已修/722"空日志"待解(16类错误已分类)；③美年体检 AI数据中台 MJ-AI-DW-2026-001：108人天10章LLD，MaxCompute/Hologres/RDS PG/OSS；④Tapestry Landing Zone：HLD 23页8领域完成，LLD PPT待做；⑤远景能源云迁移调研推进中；⑥AICCP平台收尾(Vue3/FastAPI/PG16/Redis/MinIO，三层架构，腾讯云ECS 8.153.152.218，仓库 bfliujinlong/AI-CCP，AI能力必须走Skill→Prompt→LLM→Structured Output)。

---

【2026-09-06】WorkBuddy 技能已导入本机：workbuddy-rules(全局公约+4细则)、qy-dubaifintech-bid(报价档案)、aiccp-platform(平台规范)，及文档处理 pdf/docx/xlsx/pptx/humanizer/summarize。当日 Hermes v0.21.0 完成 venv 重建+软链修复+systemd 自启(用户级 hermes-gateway.service)。

---

报价迭代模式：基线版→参考模板对齐→中英双版分文件输出；标准工作流：文档分析→PPT补充页→风险矩阵→draw.io架构图。

---

用户标准售前资料收集表=BasicInfo收集表（14 Sheet：BasicInfo收集/预算范围/迁移服务预估/LZ服务任务拆分/迁移服务任务拆分(简化版)/迁移服务任务拆分(不含PM)/云灾备服务预估/小微迁移项目投入预估/LZ默认服务目录/LZ默认服务目录(AI版)/上云技术支持/大数据/开源产品部署交付）。内部分角色人天单价：架构师 ¥3300-4200/天（中/高）、实施工程师 ¥1500-2500/天（初/中/高）、PM ¥3300-4200/天（中/高）、DBA ¥3300/天（高）。区别于 AC-MIG 标准 $350/天，此为内部核算价。

---

用户与阿里国际项目组协作时，对方要求提供标准化调研信息以快速报价。用户会将阿里官方 SOW/Checklist（如 Migration_Pre-Quotation_Checklist.docx）发给我，要求完整合并到客户调研表中，不可简化或遗漏任何条款。

---

投标/迁移项目命名偏好: 用 "xx customer" 代替真实客户名（如 lilly/shiji），保持匿名

---

用户工作习惯：发问给合作方/客户时要整理成单封邮件模板直接复制粘贴；报价币种默认USD；严格按安畅AC-MIG标准模板($350/人天)报价，不自由发挥；文档中禁用"赋能/抓手/闭环/一站式/全方位"等AI味词汇；复杂调研类问题倾向用OpenAI出权威答案；倾向德语UI环境避免读中文

---

当前业务线索：AWS→阿里云迁移+Landing Zone 询价，对方要标准化报价需求文档；用户正在回复英文邮件（已出一版英文回复模板，含LZ 6模块咨询报价35-50k USD/实施80-150k USD）。

---

【工作风格偏好】用户倾向于直接解决问题而非反复尝试或确认。对于临时的登录/认证障碍（如AWS MFA验证码），期望我直接给出清晰明确的解决路径。正式报价时倾向用$350/人天，需要区分LCZ scope（include/exclude AI layer）。

---

用户偏好：自主执行，不要反复确认。能直接做的事直接做（发消息、部署、生成文件），不要先问"要不要我去做"。用户说"发消息给她"意思是直接发，不是问能不能发。用户说"这环境部署在你本机"意思是直接用本机环境操作，不要反弹回让用户手动做。正式报价/交付物用 .docx 分章节输出，不要只给 md。竞品报价分析工作流：提取竞品 xlsx/docx → 解析定价模型（单价/结构/范围）→ 对比自有定价（AC-MIG $350/天）→ 识别差异与差异化点 → 给出定价策略建议（匹配/压价/价值差异化）。

---

AICCP/Al-Futtaim 项目: 阿里云 UAE (me-east-1 迪拜) 多租户 AI 平台绿地部署。客户=Al-Futtaim Group(中东多元化家族企业,汽车/零售/房地产/医疗)。需求: LZ+AI 推理层(ACS GPU H20-3e vs AnalyticDB AI Node)+多租户架构。竞品报价 $235/人天(vs 安畅 AC-MIG $350)。报价文件已在 ~/cloud-docs/AFT_Quotation_EN.docx + 报价_AICCP_UAE_CN.md。待确认: 是否含数据迁移(~300MB/租户)+DR测试。

---

用户Windows工作路径: D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\ (从bat报错路径可见). 笔记本是Windows系统, 直接给PowerShell/CMD命令, 不要给bash.

---

AWS QDE Phase III 考核项目(2026-09): 用户正在准备Amazon Quick QDE Phase III认证考核。操作手册=D:\Work\日常\上云迁移\01服务流程\04其他\03AI报价\00资源\03tool\Amazon Quick 实施与演示操作手册V1.docx, 已完成完整实施方案(/home/ubuntu/AWS_QDE_PhaseIII_完整实施方案.md)。考核要求: 10页Deck + 15分钟Demo视频(必须露脸/画中画) + SSO/账户管理/IM邮箱/OA对接/自动化Skill五大方向。

---

User's resource breakdown includes IaaS VMs and PaaS components (application servers and database instances). They prefer to create a migration quotation and follow the Anchnet pricing template for additional services like deployment and business tracking on AICC.