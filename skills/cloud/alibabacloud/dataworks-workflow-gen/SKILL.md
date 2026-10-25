---
name: dataworks-workflow-gen
description: "基于源 SQL / ETL 脚本自动生成 DataWorks 工作流与调度作业。覆盖 ODPS SQL、ODPS MR、Shell、Python、DI 离线同步节点；支持参数化、调度周期配置、依赖关系。"
description_zh: "DataWorks 工作流与作业生成"
description_en: "DataWorks workflow and task generation"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
trigger: ["DataWorks", "工作流", "调度", "ETL生成", "DataWorks节点", "DataStudio"]
---

# DataWorks 工作流与作业生成

把源端的 SQL / Shell / Python 脚本自动映射到阿里云 DataWorks 的工作流，配置调度周期与依赖关系。

## 工作流

### 第 1 步 源作业清点

按类型分类：

| 源类型 | DataWorks 节点 |
| --- | --- |
| SQL 文件 | ODPS SQL |
| Shell 脚本 | Shell |
| Python 脚本 | Python |
| ETL 工具（DAG） | Data Integration（DI）离线同步 |
| 调度依赖（Crontab / Airflow） | DataWorks 调度依赖 |
| 通知 / 告警 | 告警 / 通知节点 |

### 第 2 步 工作流节点拆分

按源脚本依赖关系拆分为 DAG：

```
源：load.sh → transform.py → notify.py
目标 DataWorks：
  - 节点 1：ODPS SQL（加载数据）
  - 节点 2：ODPS MR 或 Python（转换）
  - 节点 3：告警节点（运行结果通知）
```

### 第 3 步 生成工作流定义

DataWorks 工作流的核心结构：

```
{
  "name": "etl_daily",
  "schedule": {
    "cron": "00 30 02 * * ?",
    "type": "cron",
    "timezone": "Asia/Shanghai"
  },
  "nodes": [
    {
      "id": "load_orders",
      "type": "ODPS_SQL",
      "sql_file": "sql/load_orders.sql",
      "params": {"dt": "${bizdate}"},
      "depends_on": []
    },
    {
      "id": "transform_orders",
      "type": "ODPS_SQL",
      "sql_file": "sql/transform_orders.sql",
      "params": {"dt": "${bizdate}"},
      "depends_on": ["load_orders"]
    }
  ]
}
```

### 第 4 步 参数化与变量

-  `${bizdate}`：业务日期（前一天）
-  `${cyctime}`：定时时间
-  自定义参数：工作流启动时传入
-  调度配置：crontab、依赖触发、手动触发

### 第 5 步 调度依赖配置

| 调度场景 | 配置 |
| --- | --- |
| 同周期依赖 | `depends_on: [other_task_id]` |
| 跨周期依赖 | `${bizdate-1}` 参数引用 |
| 跨工作流依赖 | `cross_workflow_dependency` |
| 跨地域依赖 | `cross_region_dependency` |

### 第 6 步 输出工作流文件

```
- {workflow_name}.json：工作流定义
- {workflow_name}.yaml：人类可读版本
- nodes/{node_id}.sql：节点 SQL
- README.md：触发方式、参数说明
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 工作流定义 | JSON / YAML |
| 节点 SQL | 按节点拆分 |
| 调度依赖图 | Mermaid |
| 参数说明 | Markdown |
| 部署 README | Markdown |

## 边界

- **不做**：工作流实际部署（需 DataWorks 项目访问权限）。
- **依赖**：源作业完整、目标 DataWorks 项目已开通。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| alibabacloud-dataworks-datastudio-develop | DataWorks 节点/工作流创建、校验、部署（核心） | 已安装；本 skill 生成定义后，用它完成部署与验证 |
| alibabacloud-dataworks-metadata | 查询已有表、节点与依赖关系 | 已安装 |
| aliyun-cli skill | DataWorks OpenAPI 直调 | `aliyun dataworks ...` 先查 help |
