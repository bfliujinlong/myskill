---
name: finance-ops
description: "财务/商务核算：OPC 迁移项目报价测算、资源用量→成本核算、TCO 对比（源云 vs 目标云）、折扣与合同金额、回款与账期、预算告警。触发词：报价、成本核算、TCO、预算、折扣、合同金额、回款、账期、财务、商务核算。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [财务, 报价, 核算, TCO, 预算, 商务, 成本]
    related_skills: [business-development, presales-architect, sales, project-manager]
---

# 财务核算与商务测算（Finance Ops）

## When to Use
- 给客户做 OPC 迁移报价：资源清单 → 月费 → 折扣 → 合同金额
- 源云 vs 目标云 TCO 对比（证明迁移划算）
- 预算编制、超支预警
- 回款计划、账期、首付款比例
- 把技术配置翻译成老板看得懂的钱

## 工作方式
1. 所有数字先列**假设**（规格、时长、单价来源），再算，避免拍脑袋。
2. 用表格呈现：资源 | 规格 | 数量 | 单价 | 月费 | 年费。
3. TCO 对比给三列：现状(源云) / 目标云 / 节省额与节省比例。
4. 报价留缓冲（一般 +15%~20% 不可预见费），标注是否含税。

## 常用速查
- 云成本构成：计算(CPU/内存/走量) + 存储(块/对象/NAS) + 网络(流量/带宽/专线) + 数据库/中间件 + 迁移人工。
- 折扣通常按年框/承诺消费(commit)拿，列出可谈点。
- 回款：首付款 30%~50%，验收 40%~50%，质保金 10%~20%。
- Always Free 资源不计费，但限规格（如 OCI 2OCPU/12G、存储 200G）。

## 输出物
- 报价单（明细 + 合计 + 含税/不含税）
- TCO 对比表（源 vs 目标）
- 回款节奏表
- 预算与超支预警线
