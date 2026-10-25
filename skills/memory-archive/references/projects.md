待办提醒（周一 2026-09-08）：用户将带来 Claude 本地配置（~/.claude/ 目录）和 WorkBuddy 本地端配置，需要我统一梳理去重后导入 Hermes + 同步到各 Agent。已有 WorkBuddy 云端导出（50 Skills + 4 Rules + Memory）在 /tmp/workbuddy-export/§
【2026-09-06】WorkBuddy 主记忆已完整同步：权威原文=同目录 WORKBUDDY-MEMORY-full.md（5774字），结构化8维度=WORKBUDDY-MEMORY-structured.md。项目台账/商务基准/近期动态以该文件为准。

---

汤臣倍健团队分工：潘超胜、刘家君、丁宇文、陈铭。

---

AICCP 技术栈：Vue3/FastAPI/Docker(5容器)/PG16/Redis/MinIO/UUID PKs/RBAC；AI 开发强制 Skill→Prompt→LLM→Structured Output；部署腾讯云 ECS 8.153.152.218；仓库 bfliujinlong/AI-CCP。

---

【2026-09-10】已整合 4 个 FDE 开源项目(fdeops/fdestack/openfde/fde-guide)为统一 Skill `fde-toolkit`(~/.hermes/skills/business/fde-toolkit/)，同步到 cc/codex。核心方法论: Skills管流程执行，仓库管业务记忆。阶段模型 land→discover→plan→ship→outcome，8个客户生命周期Skills。用户正系统构建 FDE 实战能力。

---

AWS QDE Phase III 考核要求(2026-09): 交付物=10页Deck+15分钟Demo视频(必须学员头像出镜)。考核五大方向: ①SSO登录设计 ②平台账户管理 ③IM和邮箱集成 ④业务平台对接(ERP/CRM/OA) ⑤自动化流程Skill。评分: 覆盖度/原创性/准确性/深度和广度/表达力。用户已有操作手册V1(docx)+PPT V3(10页)。SSO三种方案: IdP直连(SAML)/IDC+Cognito(快速)/IAM Federation。用户倾向IDC+Cognito快速方案。落地路线: 阶段一2-4周试点→阶段二4-8周种子团队→阶段三持续规模化。

---

User shared that they are preparing for AWS QDE Phase III certification evaluation. It requires a 10-slide deck and a 15-minute demo video with the user's avatar included.

---

User prioritizes tasks that assist with AWS certification-related projects, including AWS QDE Phase III evaluation. These tasks include platforms registration, SSO login design, ERP/CRM/OA integration, and automatic Skill workflows. The user aims to create deliverables like a 10-page deck, demo video, and an online document for collaboration and submission.

---

AWS QDE Phase III 认证项目(2026-09-20): 用户正在准备 AWS QDE Phase III 认证考核。交付物：10页Deck + 15分钟Demo视频(必须出镜)。考核方向：SSO登录设计/平台账户管理/IM和邮箱集成/业务平台对接/自动化流程Skill。操作手册在 ~/cloud-docs/ 下，PPT V3 已有10页完整框架。用户要录屏交作业。

---

User wants Hermes to directly log in to Mingdao workflow system and analyze work hour records, without requesting manual exports or further input. Prefers direct execution over clarifications or queries about access.

---

Cloud browser mode failed navigating to Mingdao page due to lack of CDP endpoint from BrowserUse provider. Solution is to log in using user's credentials or request export for local analysis.

---

AWS QDE Phase III 考核项目(2026-09-20): 用户正在准备 AWS QDE Phase III 认证考核。交付物: 10页Deck(PPT) + 15分钟Demo视频(必须出镜)。考核方向: SSO登录设计/平台账户管理/IM和邮箱集成/业务平台对接(OA审批)/自动化流程Skill。操作手册: ~/cloud-docs/Amazon Quick 实施与演示操作手册V1.docx。PPT V3已有10页框架。完整实施方案: ~/AWS_QDE_PhaseIII_完整实施方案.md。用户要求: 实操全部做完后创建新的在线文档, 验收演示并录屏交作业。

---

AWS QDE Phase III 考核(2026-09-20): 用户正在准备，需要完成：①按操作手册在AWS注册配置演示 ②10页Deck(已有V3框架) ③15分钟Demo视频(需露脸)。考核方向：SSO/账户管理/IM邮箱/业务对接OA/自动化Skill。操作手册+方案已生成在 ~/AWS_QDE_PhaseIII_完整实施方案.md。