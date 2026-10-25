---
name: qy-dubaifintech-bid
description: "QY-DubaiFintech 云迁移报价项目档案：AWS→阿里云迪拜 me-east-1，76 EC2/27 DB/45 Redis/51TB/5 源区，目标 2AZ 双活。做该项目报价、AC-MIG 人天测算、中英双语 SOW 输出时触发。"
version: 1.0.0
author: jinlongliu
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [QY, 报价, DubaiFintech, 中东, me-east-1]
    related_skills: [workbuddy-rules, cloud-migration-pm]
---

# When to Use
用户提到 DubaiFintech / 迪拜 / QY 报价 / me-east-1 / 中东迁移时加载。

# 项目档案（截至 2026-09-06）
| 项 | 值 |
|---|---|
| 项目号 | QY-DubaiFintech |
| 迁移方向 | AWS → 阿里云迪拜 me-east-1 |
| 资源规模 | 76 EC2 / 27 DB / 45 Redis / 51TB 数据 / 5 源区 |
| 目标架构 | 2AZ 双活 |
| 状态 | 报价冲刺：基线版 → 参考模板对齐 → 中英双版分文件 |

# 报价输出纪律
- 定价：AC-MIG，$350/人天，必须给「角色×工作内容×人天×单价×小计」明细表
- 双语：`报价_CN.docx` 与 `Quotation_EN.docx` 分开成文件，英文版按英文商务习惯重写而非直译
- 结构：背景 → 范围与假设 → 资源评估结论 → WBS → 人天测算 → 商务条款 → 待确认清单
- 待确认清单必写：RTO/RPO、停机窗口、数据增量、第三方 License、等保/合规
- 去AI味：禁"赋能/抓手/闭环/一站式/全方位"，禁空洞开场；直接给结论和数字
- 未核实数字不得进终版；海外客户默认英文沟通，专业克制不过度承诺
