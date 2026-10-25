---
name: oracle-compat-assess
description: "Oracle 数据库到阿里云的兼容性评估。覆盖 PL/SQL 包、存储过程、触发器、序列、DBLink、Job、Scheduler、用户自定义类型、字符集、时区、特殊权限。给出 PL/SQL → PolarDB / ADAM 的兼容度与改造清单。"
description_zh: "Oracle 兼容性评估（PolarDB / ADAM / OceanBase）"
description_en: "Oracle compatibility assessment for Alibaba Cloud"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
trigger: ["oracle兼容", "oracle评估", "PL/SQL", "oracle迁移", "polarDB oracle", "ADAM", "OB Oracle兼容"]
---

# Oracle 兼容性评估

把 Oracle 数据库迁到阿里云之前，先把"搬过去之后哪些东西会跑不起来"说清楚。覆盖 PL/SQL、存储过程、触发器、序列、特殊对象类型、字符集、时区等，给出逐项改造工作量。

## 输入

-  Oracle 版本（11g / 12c / 19c / 21c）
-  目标引擎候选：阿里云 PolarDB Oracle 兼容版 / 自建 OceanBase Oracle 模式 / ADAM 评估
-  Schema 导出（DBA_OBJECTS、DBA_SOURCE、DBA_DEPENDENCIES）
-  关键存储过程与触发器清单

## 工作流

### 第 1 步 对象清点

按类型统计：

| 类型 | 统计 SQL | 关注 |
| --- | --- | --- |
| 表 | `dba_tables` | 字符集、压缩、LONG/LOB 字段 |
| 视图 | `dba_views` | 物化视图、复杂 SQL |
| 存储过程 / 函数 | `dba_procedures` | 嵌套深度、动态 SQL |
| 触发器 | `dba_triggers` | DML 触发器、DDL 触发器 |
| 序列 | `dba_sequences` | 自增策略差异 |
| 索引 | `dba_indexes` | 位图索引、反向索引 |
| 分区 | `dba_tab_partitions` | 分区策略兼容性 |
| DBLink | `dba_db_links` | 跨库依赖 |
| Job / Scheduler | `dba_jobs` / `dba_scheduler_jobs` | 调度系统迁移 |
| Materialized View | `dba_mviews` | 刷新策略 |
| 自定义类型 | `dba_types` | 对象表、嵌套表 |

### 第 2 步 PL/SQL 复杂度评估

逐存储过程评估：

| 维度 | 评估项 | 难度 |
| --- | --- | --- |
| 嵌套深度 | IF/LOOP/CURSOR 嵌套层数 | 高 = 改造难度高 |
| 动态 SQL | EXECUTE IMMEDIATE / DBMS_SQL | 高 |
| 异常处理 | WHEN OTHERS / 自定义异常 | 中 |
| 集合类型 | VARRAY / 嵌套表 / 关联数组 | 中-高 |
| 包内常量 | 包级全局变量 | 低-中 |
| Oracle 特有包 | DBMS_LOB / UTL_FILE / UTL_HTTP | 高（需替换） |

### 第 3 步 兼容性判定

按目标引擎分类：

**PolarDB Oracle 兼容版**（兼容度高）

- ✅ DDL、视图、普通 PL/SQL
- ⚠️ 高级特性：DBMS_SCHEDULER、Materialized View、Flashback
- ❌ Oracle RAC、Advanced Queuing、Oracle Streams

**OceanBase Oracle 模式**（兼容度中）

- ✅ DDL、普通 PL/SQL、序列
- ⚠️ 物化视图、Package 全局变量
- ❌ DBMS_LOB 部分包、AQ、XMLType

**ADAM 评估工具**（辅助）

-  自动化对象兼容性扫描
-  输出改造建议与代码示例

### 第 4 步 改造工作量估算

按对象类型分档：

| 对象类型 | 改造人天/百个对象 |
| --- | --- |
| 简单 DDL | 0.5 |
| 视图 | 1.0 |
| 触发器 | 3.0 |
| 存储过程（无嵌套） | 2.0 |
| 存储过程（嵌套） | 5.0–10 |
| 包（Package） | 5.0 |
| 自定义类型 | 8.0 |

### 第 5 步 输出报告

```
- 对象清单（按类型分组）
- 兼容度分布（✅/⚠️/❌）
- 高风险对象清单（含位置、风险点、改造建议）
- 改造工作量估算
- 目标引擎选型建议
- 迁移路径建议（先兼容版本 → 后续优化）
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 兼容性评估总报告 | Markdown |
| 对象清单 | Excel（含兼容度等级） |
| 高风险对象清单 | Excel（含改造建议） |
| 改造工作量估算 | Excel |
| 目标引擎选型建议 | Markdown |

## 边界

- **不做**：实际 PL/SQL 改写（在 ADAM 输出基础上由开发团队执行）。
- **依赖**：Schema 导出需客户提供，对象权限（密码、Wallet 等）由客户提供。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 确认目标 PolarDB 版本与兼容模式 | `aliyun polardb DescribeDBClusters`；ADAM 相关 product 先从 `aliyun --help` 产品列表确认再调用 |
| find-skills skill | 检索 Oracle 专项评估 skill | 本地市场优先 |
