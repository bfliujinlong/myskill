---
name: personal-collections
description: 管理 ~/personal/collections/ 个人收藏素材（图片/物件/灵感）。自动建目录、复制原图、生成带品类/材质/寓意的说明 .md。与 work 素材库 ~/cloud-docs/ 隔离。触发词：收藏/存个人/我的收藏/收进个人/这件东西存个人。
version: 0.1.0
author: Hermes Agent
license: MIT
category: personal
tags: [收藏, 个人, 素材]
related_skills: [personal-life]
---

# 个人收藏管理（Personal Collections）

把用户发来的图片/物件**存到个人区** `~/personal/collections/`，并自动生成说明文件。区别于工作素材库 `~/cloud-docs/`（客户方案/报价/架构图）。

## When to Use
- 用户说「存个人」「放个人文件夹」「收藏这件」「我的东西」→ 落 `~/personal/collections/`
- 工作类素材（客户资料、架构图、报价单）→ 走 `~/cloud-docs/`，**不进此技能**

## 流程
1. 确认 `~/personal/collections/` 存在，不存在则 `mkdir -p`
2. 复制原图/文件，命名 `主题_特征.扩展名`（中文名即可，如 `木梳_鱼戏莲_红木.jpg`）
3. 同目录生成 `主题_特征_说明.md`，含：
   - 图片路径
   - 物理特征（形制/材质/工艺/表面）
   - 品类定位（功能/材质/纹样/工艺）
   - 纹样寓意（如有）
   - 备注（来源、鉴定限制）

## 示例（已落地）
- `木梳_鱼戏莲_红木.jpg` + `木梳_鱼戏莲_红木_说明.md`
  - 红木类硬木、鱼戏莲纹、手工浮雕宽齿按摩梳

## 注意
- 个人收藏不混入 `~/cloud-docs/` 工作区
- 材质/树种鉴定受限图片时，明确标注「需实物闻味/沉水/截面检测」，不臆断
