---
name: sql-compatibility-assess
description: "对源 SQL 脚本进行复杂度分析与跨引擎兼容性评估。覆盖 Oracle、MySQL、PostgreSQL、SQL Server、Hive、Spark 等引擎到阿里云目标（RDS / PolarDB / Hologres / MaxCompute）的迁移场景。给出每条语句的兼容度等级与改造建议。"
description_zh: "SQL 兼容度评估与迁移风险量化"
description_en: "SQL compatibility and cross-engine assessment"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
trigger: ["SQL兼容", "SQL评估", "SQL改造", "跨引擎", "SQL迁移", "SQL审计", "SQL风险", "compatibility"]
---

# SQL 兼容度评估

把"这些 SQL 能不能直接搬到阿里云、不能的话要改多少"这件事说清楚。给出每条语句的兼容度等级、改造工作量估算、风险等级，作为后续迁移方案与报价的输入。

## 输入

-  源数据库类型（Oracle / MySQL / PostgreSQL / SQL Server / Hive / Spark）
-  目标引擎：阿里云 RDS（MySQL/PG/SQL Server）、PolarDB（MySQL/PG/Oracle 兼容版）、Hologres、MaxCompute
-  待评估的 SQL 文件或脚本目录
-  采样规则：全量 / 抽样（默认抽样 5% 但不少于 200 条）

## 工作流

### 第 1 步 抽取 SQL

- 单文件读取 → 解析为语句列表
- 目录递归：扩展名 `.sql`、`.hql`、存储过程文件
- 跳过注释、空行；保留事务控制语句
- 对超大脚本（>10k 行）分块读取，避免一次加载到内存

### 第 2 步 复杂度评分

每条语句按四个维度打分（0–10）：

| 维度 | 评估项 |
| --- | --- |
| 语法复杂度 | 嵌套深度、子查询层数、函数调用数 |
| 对象引用 | 涉及表/视图/序列/包的数量 |
| 控制流 | 存储过程、触发器、动态 SQL |
| 语义复杂度 | 跨库查询、分布式事务、递归 CTE |

综合分 = 各维度加权和。

### 第 3 步 兼容性评估

按目标引擎给出每条语句的兼容度：

| 等级 | 含义 | 改造工作量 |
| --- | --- | --- |
| ✅ 直接兼容 | 目标引擎原生支持，零改动 | 0 |
| ⚠️ 语法兼容 | 自动等价转换即可 | < 0.5 人天/百条 |
| ⚠️ 语义差异 | 行为不一致，需手工改写 | 1–5 人天/百条 |
| ❌ 不兼容 | 目标引擎无对应能力 | 需替换方案 |

判定依据：

- Oracle → PolarDB Oracle 兼容版：兼容度高，主要注意 PL/SQL 包
- Oracle → MySQL/PG：重点排查序列、CONNECT BY、ROWNUM
- MySQL → PolarDB/MySQL：基本兼容，注意 SQL_MODE 与字符集
- SQL Server → 阿里云：注意 T-SQL 特性（OUTPUT、APPLY、PIVOT）
- Hive/Spark → MaxCompute：注意 Hive UDF、自定义 SerDe、Spark RDD API

### 第 4 步 风险汇总

按语句类型汇总：

| 类别 | 数量 | 占比 | 平均风险分 |
| --- | --- | --- | --- |
| DDL | 120 | 12% | 3.2 |
| DML（INSERT/UPDATE/DELETE） | 680 | 68% | 2.1 |
| 查询 SELECT | 180 | 18% | 5.4 |
| 存储过程 | 20 | 2% | 8.7 |

高风险语句 TOP 10 列表（含位置、风险分、改造建议）。

### 第 5 步 输出报告

```
- 兼容度分布饼图（按等级）
- 复杂度分布直方图
- 高风险语句清单（位置 + 风险点 + 改造建议）
- 改造工作量估算（按等级分档）
- 目标引擎选型建议（如多引擎混合）
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 评估总报告 | Markdown / PDF |
| 逐条语句评估表 | Excel / CSV（含 ID、位置、复杂度、兼容度、改造建议） |
| 高风险语句清单 | Markdown |
| 改造工作量估算表 | Excel |

## 边界

- **不做**：动态 SQL 的运行时模拟（无法静态分析）。
- **依赖**：Oracle 兼容度评估需要客户提供具体 Oracle 版本号、目标 PolarDB 版本。
- **存储过程**：复杂度高时建议抽样评估，给出"全量改造"的工作量区间而非逐条改写。
- **跨方言自动转换**：可在报告中给出等价改写示意，但不出具"自动转换后脚本"作为最终交付。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 确认目标实例规格与引擎版本 | `aliyun rds DescribeDBInstances`、`aliyun polardb DescribeDBClusters`（只读 Describe*） |
| find-skills skill | 检索特定数据库引擎的专项评估 skill | 本地市场优先 |
