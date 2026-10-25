---
name: pcs-presales-ps
description: "PCS上云服务交付体系知识库。从飞书 Wiki「上云服务交付体系」迁移至 Knodo。覆盖售前Bidding和交付Professional Service两大业务领域，按00-99目录纪律组织素材。"
version: 1.0.0
author: jinlongliu
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pcs, presales, delivery, professional-service, 上云, 云迁移, 阿里云MSP, 安畅网络]
    related_skills: [presales-architect, solution-delivery, spreadsheet-delivery, project-manager, fde-deployment]
---

# PCS上云服务交付体系知识库 (pcs-presales-ps)

## 背景

从飞书 Wiki「上云服务交付体系」迁移至 Knodo，2026-08-28。
源文档：https://anchnet.feishu.cn/wiki/XERPwZrU8iWGuNkko8tcK79mnAg（space: 7200267672453070849）

## 与 pcs-presales 的关系

- **pcs-presales** = 售前 Bidding 知识库（应标、报价、Offering 叙事）
- **pcs-presales-ps** = 交付 Professional Service / 上云交付 知识库（交接入场、WBS、周报、巡检、RCA、验收、Transition）

两者共享同一套目录纪律与命名规范；交付侧素材不进售前库，反之亦然。

## 目录结构

上云服务交付体系/
├── 00-系统说明与索引/                    📋 骨架（本 README + 目录规范）
├── 01-标准模板/ (9子目录)                📋 骨架
├── 02-Offering素材/                      📋 骨架（待按交付服务包细分）
├── 03-交付场景素材/
│   ├── 01-New-Delivery/                  ⚪️ 空
│   ├── 02-Transition-接管/               ⚪️ 空
│   └── 03-续约续服/                      ⚪️ 空
├── 04-脱敏案例库/                         ⚪️ 空
├── 05-客户问题与FAQ素材/                  ⚪️ 空
├── 06-项目材料-受限/                      ⚪️ 空
├── 07-公司资信与团队/ (2子目录)           📋 骨架
├── 97-训练营试运行材料/ (5子目录)          📋 骨架
├── 98-待整理素材/                         ⚪️ 空
└── 99-归档与废弃素材/                     ⚪️ 空

## 格式规范

- .md — Markdown，AI检索/Git版本追踪
- .docx — 飞书在线文档导出，保留原始排版
- 上传文件保持原格式 (pdf/pptx/xlsx)

## 已知问题

飞书端该 wiki 根节点正文为空壳（只有标题），全部内容在子页面树中；迁移进度以子页面同步率为准。

## 使用方法

本 skill 目录提供目录结构框架。具体素材内容需要从飞书 Wiki 手动迁移或通过 API 抓取。

### 子页面获取方式

1. 通过飞书 API 遍历子页面节点
2. 或手动从飞书导出各子页面的 docx
3. 放入对应目录

### 权限要求

飞书连接器需要 wiki:wiki:readonly / wiki:node:read / wiki:node:retrieve / search:docs:read scope 才可遍历 wiki 子节点。
