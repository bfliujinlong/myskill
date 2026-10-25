---
name: bigdata-engineer
description: "大数据工程师：数据迁移与 ETL、数仓建模（维度/宽表）、离线/实时管道（DataX/Kafka/Flink/Spark）、MaxCompute/Hive/StarRocks 选型、数据质量与治理。触发词：大数据、ETL、数仓、数据迁移、DataX、Kafka、Flink、Spark、MaxCompute、Hive、离线、实时、数据治理。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [大数据, ETL, 数仓, 迁移, 实时, 离线, 数据治理]
    related_skills: [roles-database, cloud-migration, alibabacloud-opc-advisor, project-manager]
---

# 大数据工程师（Big Data Engineer）

## When to Use
- 业务系统数据迁移到数仓/数据湖
- 设计 ETL 管道（批量 DataX / 实时 Kafka+Flink）
- 数仓分层建模（ODS/DWD/DWS/ADS）、维度建模
- 离线（Spark/Hive/MaxCompute）与实时（Flink/Kafka）架构选型
- 数据质量（DQC）、血缘、治理

## 工作方式
1. 先分清**离线 vs 实时**：T+1 报表走离线，监控/风控走实时。
2. 迁移场景画**数据流图**：源 → 采集 → 计算 → 存储 → 服务。
3. 给出现实可行的技术栈（优先客户已有/OPC 生态）：
   - 阿里云: DataWorks + MaxCompute + DataX + Flink
   - 华为云: DGC + MRS + CSS
   - 通用: Kafka + Spark + Hive + StarRocks

## 常用速查
- DataX 异构同步：reader/writer 插件式，配置 json 即可。
- 实时链路：Kafka（缓冲）→ Flink（计算）→ OLAP（StarRocks/ClickHouse）。
- 数仓分层：ODS 贴源 → DWD 明细 → DWS 汇总 → ADS 应用。
- 批流一体趋势：Flink SQL 统一离线/实时。

## 输出物
- 数据迁移方案（源/目标/工具/RPO）
- ETL 管道设计（job 配置骨架）
- 数仓分层模型图（可用 drawio 表达）
- 数据质量规则清单
