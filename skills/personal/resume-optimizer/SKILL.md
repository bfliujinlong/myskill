---
name: resume-optimizer
description: 简历优化与多平台投递辅助（个人区 skill，与 work 技能隔离）。覆盖：简历起草/优化（中文智联51job猎聘、海外 LinkedIn/Workday）、按平台格式适配、AI 起草求职信与打招呼话术、投递进度追踪。铁律：只做「AI 起草 + 你逐条确认发送」，严禁无人值守批量自动投递（违反各平台 ToS、必封号）。触发词：优化简历/更新简历/帮我投/智联/51job/猎聘/LinkedIn/Workday/海外求职/打招呼话术。
version: 0.1.0
author: Hermes Agent
license: MIT
category: personal
tags: [简历, 求职, 投递, 个人]
related_skills: [personal-life]
---

# 简历优化与多平台投递辅助（Resume Optimizer）

帮助用户优化简历、按平台适配格式、起草求职信/打招呼话术，并**辅助**投递。
属于 personal/ 生活区，与 work 技能（售前/云迁移/FDE/商务）隔离。

## ⚠️ 铁律（不可违反）
- **只做「AI 起草 + 用户逐条确认发送」**。
- **严禁无人值守批量自动投递**：脚本后台自动投 1000 份 / 睡眠时自动投 = 明确违反 LinkedIn ToS clause 8.2 / 智联51job猎聘反爬风控，必封号且属灰产。本 skill 不提供此能力。
- 投递动作必须由用户本人点击 Send / 提交。AI 最多生成"填表内容建议"供用户复制粘贴。

## When to Use
- 「优化/更新简历」→ 读取 `~/personal/resume/` 源文件，按平台重写
- 「帮我投智联/51job/猎聘」→ 生成该平台版简历文本 + 打招呼话术，用户自行登录平台粘贴提交
- 「LinkedIn/Workday 海外求职」→ 生成英文 resume + cover letter，用户自行在平台提交
- 「写打招呼话术」→ 按岗位 JD 生成个性化消息

## 平台格式适配要点
| 平台 | 语言 | 格式要点 |
|------|------|---------|
| 智联/51job/猎聘 | 中文 | 结构化（个人信息/求职意向/工作经历/项目/教育），控制 2 页内，关键词匹配 JD |
| LinkedIn | 英文 | 摘要式 headline + experience bullets（量化成果），适配 ATS |
| Workday | 英文 | 按各公司独立字段填，经历用 action verb + 量化 |
| 海外通用 | 英文 | 1 页 resume + cover letter |

## 工作流
1. 确认 `~/personal/resume/` 是否有源文件；无则向用户索取或基于职业画像起草
2. 读取目标岗位 JD（用户给链接/原文）
3. 按平台生成适配版简历 + 求职信/话术（写入 `~/personal/resume/<平台>_<日期>.md` 或 .docx）
4. **交还用户**：明确告知"请登录平台自行粘贴提交"，不代投
5. 维护 `~/personal/resume/投递追踪.md` 记录投递状态

## 输出位置
- 源/产物：`~/personal/resume/`
- 投递记录：`~/personal/resume/投递追踪.md`

## 注意
- 不碰用户密码、不登录任何招聘平台账号（本机也无浏览器持久会话）
- 简历含个人信息，仅存本地 `~/personal/`，不外发工作区
- 量化成果须真实，不编造数据（编造=失信风险）
