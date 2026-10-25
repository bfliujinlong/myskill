---
name: personal-life
description: 个人生活事务总入口（与 work 类 skill 物理隔离在 skills/personal/ 下）。覆盖：家人健康管理（接 medical-advisor）、个人收藏素材管理（接 personal-collections）、日常个人事务整理。触发词：个人/生活/健康/家人/收藏/我的东西/生活安排。
version: 0.1.0
author: Hermes Agent
license: MIT
category: personal
tags: [生活, 健康, 收藏, 个人]
related_skills: [medical-advisor, personal-collections]
---

# 个人生活事务（Personal Life）

用户「个人/生活」维度的事务入口。与 work/ 下的售前、云迁移、FDE、商务等技能**隔离**，只在用户谈生活、健康、收藏、家庭时使用。

## When to Use
- 用户聊**家人健康/病历/报告解读** → 调 `medical-advisor`（铁律：不诊断、不处方、急症强制引导 120/急诊）
- 用户要**收藏/保存图片物件/建素材库** → 调 `personal-collections`（落到 `~/personal/collections/`）
- 用户谈**个人生活安排、非工作事务** → 在本入口处理，不混入 work 技能链

## 边界
- 工作类技能（presales-architect / cloud-migration / fde-deployment / solution-delivery / spreadsheet-delivery / business-* / roles-*）**不在此入口加载**
- 用户说「工作」「客户」「方案」「报价」「迁移」等 → 走 work 链路，不调本技能
- `~/personal/` 是用户个人区（health/ 病历、resume/ 简历、collections/ 收藏），与工作区 `~/cloud-docs/` 分开

## 子技能
- `medical-advisor`：健康信息整理 + 通俗化解读 + 风险点标注 + 就医引导
- `personal-collections`：个人收藏素材的增删查 + 自动加说明文件

## 注意
- 个人健康信息属敏感数据，仅存本地 `~/personal/`，不外发、不入工作文档
- 医疗类严格守 medical-advisor 的「不诊断不处方」红线
