---
name: memory-archive
description: Use when 需要查询历史记忆明细(飞书/OCI账单/dsh隧道/投标模板/项目/环境配置等)但主记忆已精简, 按需从references/读取, 不占每轮注入token.
---

# Memory Archive

主记忆(`~/.hermes/memories/MEMORY.md`)已精简到 ~1KB, 只存高频跨会话事实。
历史明细按主题归档在本目录, **需要时才读**, 不每轮注入。

## 索引

| 文件 | 内容 | 何时读 |
|---|---|---|
| `feishu.md` | 飞书权限/app/多维表/MCP 全部踩坑细节 | 处理飞书读写、报 230002/99991672 |
| `oci-billing.md` | OCI CLI 路径、账单查询、磁盘清理 | 查费用/账单/磁盘 |
| `dsh-tunnel.md` | dsh/Cloudflare 隧道/nginx/域名 | 配公网访问、隧道故障 |
| `model-routing-history.md` | 模型路由演变史(107条) | 排查模型故障时看规律, **勿照抄旧配置** |
| `bid-templates.md` | 投标/报价/SOW/技术标模板经验 | 做标书报价 |
| `projects.md` | 各项目档案(AICCP/泉峰/AIOps/QDE等) | 接手具体项目 |
| `env-config.md` | CLI 路径/端口/cron/GitHub 备份 | 环境排障 |
| `personal-family.md` | 孩子科创/课件/简历 | 个人事务 |
| `channels.md` | Telegram/微信/邮件/Twilio 通道配置 | 通道故障 |
| `fde-methodology.md` | FDE 方法论要点 | 方案设计 |

## 维护原则

- 新记忆先判断: **高频跨会话事实** → 写 MEMORY.md; **一次性/细节** → 写这里对应文件
- MEMORY.md 硬上限 2200 chars, 超限会让每轮系统提示暴涨
- 禁止把"已执行XX/已交付XX"这类日志写进记忆(2026-09 曾污染 6.5KB)
