---
name: sql-to-hologres
description: "把 Oracle / MySQL / PostgreSQL / Hive / Spark SQL 转换为阿里云 Hologres 兼容 SQL。处理函数差异、类型映射、JOIN 语法、窗口函数、分页语法。"
description_zh: "SQL 转换到 Hologres（兼容 PG / 实时数仓）"
description_en: "SQL conversion to Hologres"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
trigger: ["Hologres", "SQL转换", "sqlgate-to-hologres", "PG兼容", "实时数仓", "SQL改写"]
---

# SQL 转换到 Hologres

把其他数据库引擎的 SQL 转换为阿里云 Hologres 兼容语法。Hologres 兼容 PostgreSQL 协议，所以主要是 Oracle / MySQL / Hive 语法到 PG 系的转换。

## 工作流

### 第 1 步 源引擎识别

按输入 SQL 方言判定：

| 源 | 特征 |
| --- | --- |
| Oracle | `||` 字符串拼接、`NVL`、`DECODE`、`CONNECT BY` |
| MySQL | `` ` `` 反引号、`IFNULL`、`GROUP_CONCAT`、`LIMIT m, n` |
| PostgreSQL | 已经接近 Hologres 兼容，重点检查扩展特性 |
| Hive / Spark | 大量 `regexp_*`、Lateral View、窗口函数差异 |
| SQL Server | `TOP n`、`ISNULL`、`+` 字符串拼接 |

### 第 2 步 类型映射

| 源类型 | Hologres 类型 | 备注 |
| --- | --- | --- |
| NUMBER(p,s) | `NUMERIC(p,s)` | Hologres 不支持任意精度，用 NUMERIC |
| VARCHAR2 | `VARCHAR` | 同 |
| CLOB / TEXT | `TEXT` | 同 |
| BLOB / BYTEA | `BYTEA` | Hologres 限制单行 1MB |
| DATE | `TIMESTAMP` | Hologres DATE 含时区 |
| TIMESTAMP | `TIMESTAMP` | 同 |
| INT | `INTEGER` | 同 |
| BIGINT | `BIGINT` | 同 |
| DECIMAL | `NUMERIC` | 同 |
| BOOLEAN | `BOOLEAN` | 同 |

### 第 3 步 函数替换

| 源 | Hologres |
| --- | --- |
| Oracle `NVL(a, b)` | `COALESCE(a, b)` |
| Oracle `DECODE(...)` | `CASE WHEN ... THEN ... END` |
| Oracle `SYSDATE` | `CURRENT_TIMESTAMP` |
| Oracle `ROWNUM` | `ROW_NUMBER() OVER()` |
| Oracle `CONNECT BY` | 递归 CTE（`WITH RECURSIVE`） |
| Oracle `DUAL` | 直接 `SELECT ...` 不带 FROM |
| MySQL `GROUP_CONCAT` | `STRING_AGG` |
| MySQL `LIMIT m, n` | `LIMIT n OFFSET m` |
| Hive `regexp_extract` | `regexp_matches`（PG） |
| Hive `regexp_replace` | `regexp_replace`（PG 同名） |
| Hive `unix_timestamp(str)` | `EXTRACT(EPOCH FROM str::timestamp)` |
| Hive `from_unixtime(ts)` | `to_timestamp(ts)` |
| Hive `collect_list` | `array_agg` |
| Hive `LATERAL VIEW EXPLODE` | `UNNEST()` |

### 第 4 步 JOIN 与子查询

Hologres 要求：

- JOIN 必须显式 `JOIN ON` 或 `USING`，禁止隐式 JOIN
- 子查询必须有别名
- 关联子查询可改写为 CTE，提升可读性

### 第 5 步 窗口函数

Hologres 兼容 PG 窗口函数：

```sql
-- Hive / MySQL
SELECT id, ROW_NUMBER() OVER (PARTITION BY uid ORDER BY ts DESC) rk
FROM events;

-- Hologres（兼容，无需修改）
SELECT id, ROW_NUMBER() OVER (PARTITION BY uid ORDER BY ts DESC) rk
FROM events;
```

注意：Hologres 在 `ORDER BY` 列上要求有索引或排序键，否则性能差。

### 第 6 步 输出对比报告

```
- 转换条目数：N 条 SQL
- 自动转换：A 条（高置信度）
- 人工标注：B 条（需手工改造）
- 不可转换：C 条（业务层改造）

附逐条对照：源 SQL + 目标 SQL + 改造说明
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 转换总报告 | Markdown |
| 逐条 SQL 对照表 | Excel（源 / 目标 / 说明） |
| 函数替换速查表 | Markdown |
| 不可转换 SQL 清单 | Markdown（含业务建议） |

## 边界

- **不做**：动态 SQL 的运行时改写。
- **依赖**：源 SQL 完整、上下文明确（库表结构已知）。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 查询 Hologres 实例与数据库 | `aliyun hologram ...` 先查 help；建表等 DDL 变更先 preview |
| find-skills skill | 检索 SQL 转换专项 skill | 本地市场优先 |
