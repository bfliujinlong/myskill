---
name: ddl-compat-check
description: "检测 SQL DDL 语句（CREATE / ALTER / DROP / TRUNCATE / RENAME / COMMENT）在阿里云目标引擎（RDS / PolarDB / Hologres / MaxCompute）上的兼容性，标记不兼容项并给出等价改写建议。"
description_zh: "DDL 兼容度检测与等价改写"
description_en: "DDL compatibility check and rewriting"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
trigger: ["DDL兼容", "DDL检测", "DDL审计", "DDL迁移", "CREATE TABLE迁移", "ALTER TABLE迁移"]
---

# DDL 兼容度检测

DDL（Data Definition Language）是数据库迁移里最容易被低估的部分。一条 DDL 不兼容可能导致整个表建不出来。本 skill 集中检测 DDL 在阿里云目标引擎上的兼容性。

## 工作流

### 第 1 步 抽取 DDL

从 SQL 脚本中分离 DDL 与 DML：

| 类别 | 关键字 |
| --- | --- |
| DDL | `CREATE` / `ALTER` / `DROP` / `TRUNCATE` / `RENAME` / `COMMENT ON` / `GRANT` / `REVOKE` |
| DML | `INSERT` / `UPDATE` / `DELETE` / `SELECT` / `MERGE` |
| DCL | `GRANT` / `REVOKE` / `SET ROLE` |

### 第 2 步 按目标引擎检测

**目标：RDS MySQL / PolarDB MySQL**

| 源 | 兼容度 | 说明 |
| --- | --- | --- |
| Oracle `VARCHAR2` | ⚠️ | 替换为 `VARCHAR` |
| Oracle `NUMBER` | ⚠️ | 替换为 `DECIMAL` / `INT` |
| MySQL `ENGINE=InnoDB` | ✅ | 默认 |
| MySQL `PARTITION BY RANGE` | ✅ | 注意最大分区数 |
| MySQL `FOREIGN KEY` | ✅ | 注意引擎一致性 |
| Oracle `CREATE INDEX ... TABLESPACE` | ❌ | MySQL 无 TABLESPACE 概念 |

**目标：PolarDB PostgreSQL / Hologres**

| 源 | 兼容度 | 说明 |
| --- | --- | --- |
| MySQL `ENGINE=InnoDB` | ❌ | PG 无此语法 |
| Oracle `CREATE SEQUENCE` | ✅ | PG 同 |
| Oracle `VARCHAR2` | ⚠️ | 替换为 `VARCHAR` |
| Oracle `NUMBER(p,s)` | ✅ | 用 `NUMERIC(p,s)` |
| MySQL `TINYINT(1)` | ⚠️ | PG 用 `BOOLEAN` |
| MySQL `ON UPDATE CURRENT_TIMESTAMP` | ⚠️ | PG 用触发器实现 |

**目标：MaxCompute**

| 源 | 兼容度 | 说明 |
| --- | --- | --- |
| MySQL / Oracle DDL | ✅ | 都支持，但要注意分区写法 |
| Hive `PARTITIONED BY` | ✅ | 同 |
| Oracle `CREATE INDEX` | ❌ | MaxCompute 不支持二级索引 |
| Oracle `CREATE VIEW ... WITH READ ONLY` | ⚠️ | 去掉 `WITH READ ONLY` |

### 第 3 步 输出报告

```
- DDL 总数：N 条
- 兼容度分布：
  ✅ 直接兼容：A 条
  ⚠️ 语法兼容：B 条（自动改写）
  ❌ 不兼容：C 条（手工改造）
- 不兼容项 TOP 10（含位置、改造建议）
- 改造工作量估算
```

### 第 4 步 自动改写

针对高置信度兼容项，输出改写后的 DDL：

```sql
-- 源（Oracle）
CREATE TABLE orders (
  id NUMBER(10) PRIMARY KEY,
  status VARCHAR2(20),
  created_at DATE DEFAULT SYSDATE
) TABLESPACE users;

-- 目标（PolarDB MySQL）
CREATE TABLE orders (
  id DECIMAL(10) PRIMARY KEY,
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| DDL 兼容度报告 | Markdown |
| 逐条 DDL 评估表 | Excel |
| 自动改写结果 | SQL（按引擎分类） |
| 不兼容改造清单 | Markdown |

## 边界

- **不做**：DDL 实际执行（需 DBA 在测试环境验证）。
- **依赖**：源 SQL 完整、目标引擎版本明确。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 确认目标引擎版本与参数 | rds / polardb / hologram 的 Describe* 只读查询 |
| find-skills skill | 检索 DDL 审计专项 skill | 本地市场优先 |
