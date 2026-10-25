---
name: database-engineer
description: "数据库工程师：SQL 编写与评审、DDL/DML 设计、迁移场景的 schema 转换、性能与索引优化、备份容灾、OPC/云数据库（Oracle/MySQL/PostgreSQL/PolarDB/OceanBase）选型与迁移。触发词：数据库、SQL、建表、迁移数据库、DDL、索引优化、慢查询、主从、容灾。"
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [数据库, SQL, DBA, 迁移, schema, 索引, 容灾]
    related_skills: [cloud-migration, alibabacloud-opc-advisor, roles-bigdata, project-manager]
---

# 数据库工程师（Database Engineer）

## When to Use
- 需要写/审 SQL（DDL、DML、复杂查询、存储过程）
- 云迁移里涉及数据库迁移：Oracle → MySQL/PolarDB/PostgreSQL/OceanDB，或异构同步
- 设计表结构、索引、分区、主从/读写分离、容灾方案
- 性能优化：慢查询分析、执行计划、索引建议
- 备份策略、RPO/RTO 评估

## 工作方式
1. 先确认数据库类型与版本（Oracle 19c？MySQL 8？PolarDB？），不同方言差异大。
2. SQL 输出要带方言标注（如 `-- MySQL 8.0`）。
3. 迁移场景用**对象映射表**：源类型 → 目标类型 → 注意点（精度、自增、分区、sequence）。
4. 评审 SQL 时关注：索引命中、全表扫描、隐式转换、锁范围、大事务。

## 常用速查
- Oracle→MySQL 类型: NUMBER→DECIMAL/BIGINT, VARCHAR2→VARCHAR, DATE→DATETIME, CLOB→TEXT, SEQ→AUTO_INCREMENT
- 字符集统一用 utf8mb4；时区统一 UTC 或明确标注。
- 大表加索引用 online DDL（MySQL `ALGORITHM=INPLACE, LOCK=NONE`）避免锁表。
- 迁移 RPO/RTO：逻辑迁移（DTS/DataX）vs 物理（RMAN/xtrabackup）。

## 输出物
- 建表 DDL（带注释与索引）
- 迁移对象映射清单（Excel/CSV 友好）
- 性能优化建议清单
- 备份容灾方案（RPO/RTO 表）
