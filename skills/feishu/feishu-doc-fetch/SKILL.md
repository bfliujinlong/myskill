---
name: feishu-doc-fetch
description: "读飞书 wiki/docx 链接并整理内容. Use when 用户发飞书文档/wiki链接要读内容或梳理纪要."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [feishu, wiki, docx, fetch]
    related_skills: [feishu-bitable-access]
---

# 飞书文档读取（wiki / docx 链接）

## When to Use

用户发飞书链接（wiki 或 docx）要读内容、梳理纪要、提取信息时按此流程，不要先问权限。

## 读取流程

1. **docx 链接**（`/docx/<doc_token>`）：直接 `mcp__feishu_mcp__fetch_doc` 传完整 URL 即可，一步到位。
2. **wiki 链接**（`/wiki/<wiki_token>`）：wiki token ≠ 文档 token，需两步：
   - 先 `fetch_doc` 传 wiki URL 或裸 token → 返回里含节点解析出的真实 `obj_token`/`doc_id`；
   - 再 `fetch_doc` 传该 obj_token 读正文。
3. **节点类型判别**：解析结果 `obj_type` 为 `box`/`Unknown` 或非 docx 类型时，MCP 代理读不了（wiki 节点可能是表格/画板/文件容器，不是文档），不是权限问题，换参重试无意义。

## 降级路径（用户规则：读不了就装对应 CLI，不要报死）

MCP 读不了的节点类型，按序试：
1. 告知用户节点类型不可读，问它实际是什么（文档/表格/思维笔记）；
2. 若是多维表格 → 走 feishu-bitable-access 技能；
3. 用户确认需要时安装对应飞书 CLI 再取——用户明确说过"如果不能读 安装对应飞书 cli"，直接动手装而不是回复做不到。

## 坑
- `web_extract` 抓飞书 wiki/docx 只会拿登录页，别浪费一轮。
- wiki 解析返回的 obj_token 可能本身也是另一个 wiki 层级，需再解析一层。
- 纪要整理类任务：读全正文后按"基本信息/核心问题按人归类/分工/决策/待办按归属"结构输出，待办要标到具体人。
