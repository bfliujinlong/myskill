---
name: bigdata-stress-test
description: "对大数据组件（Hive / Spark / Flink / MaxCompute / Hologres / OSS）进行压测，验证集群在预期负载下的稳定性、性能基线、扩展性。覆盖数据准备、压测脚本、监控指标、报告生成。"
description_zh: "大数据组件压测与性能基线"
description_en: "Big data stress testing and benchmarking"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
trigger: ["大数据压测", "性能基线", "压测报告", "stress test", "benchmark", "性能测试"]
---

# 大数据压测

对阿里云大数据组件做端到端压测，产出性能基线、瓶颈分析、扩展建议。

## 适用组件

-  MaxCompute（SQL / MR / Spark）
-  Hologres（实时数仓）
-  EMR（Hive / Spark / Flink / Kafka）
-  OSS / Data Lake
-  自建 Hadoop / CDH / HDP

## 工作流

### 第 1 步 压测目标设定

按四类目标分别设计：

| 目标 | 关注 |
| --- | --- |
| **容量基线** | 当前集群能跑多大量 |
| **稳定性** | 7×24 跑是否稳定（泄漏、漂移） |
| **扩展性** | 加节点后性能线性增长吗 |
| **故障恢复** | 节点故障后多久恢复 |

### 第 2 步 数据准备

按 3 类数据生成：

```
- 真实数据脱敏：从生产环境采样、清洗
- 合成数据：根据业务模型生成（数量、分布、关联关系）
- 标准数据集：TPC-H / TPC-DS / YCSB / BigBench
```

数据规模按预期业务量 × 3–5 倍准备。

### 第 3 步 压测场景设计

按真实业务组合场景：

| 场景类型 | 例子 |
| --- | --- |
| 单作业 | 单个 ETL、单个查询 |
| 批跑 | 100 个并发 ETL |
| 高并发查询 | 1000 QPS 实时查询 |
| 混合负载 | ETL + 实时查询 同时跑 |

### 第 4 步 压测工具

| 组件 | 工具 |
| --- | --- |
| MaxCompute | Tunnel SDK + 自研脚本 |
| Hologres | PG Bench + 自研脚本 |
| EMR Spark | spark-perf / spark-bench |
| EMR Hive | hive-bench / tpch-hive |
| Flink | flink-bench / Nexmark |
| OSS | ossbench |

### 第 5 步 监控指标

按四类指标：

| 类别 | 指标 |
| --- | --- |
| 资源 | CPU、内存、磁盘 IO、网络 IO |
| 作业 | 运行时长、成功率、排队时长 |
| 业务 | QPS / TPS、RT 平均/95/99、错误率 |
| 资源效率 | 单作业 CPU 利用率、内存利用率 |

### 第 6 步 压测执行

```
阶段 1：环境校验（集群健康、数据就绪）
阶段 2：基线测试（单作业、低并发）
阶段 3：压力测试（目标并发 × 1.5）
阶段 4：极限测试（持续加压到系统瓶颈）
阶段 5：恢复测试（降压后系统能否恢复）
```

每阶段 ≥ 30 分钟，观察是否稳态。

### 第 7 步 报告输出

```
- 压测环境说明
- 数据准备说明
- 场景与负载
- 监控指标（图表 + 原始数据）
- 瓶颈分析（哪类资源先到上限）
- 扩展建议（加节点 / 调配置 / 改架构）
- 结论与建议配置
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 压测报告 | Markdown / PDF |
| 监控指标原始数据 | CSV / Parquet |
| 监控图表 | PNG / Mermaid |
| 扩展建议 | Markdown |
| 复现脚本 | Bash / Python |

## 边界

- **不做**：对生产环境的真实负载测试（压测必须独立环境）。
- **依赖**：阿里云压测资源开通、压测数据集生成权限。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| aliyun-cli skill | 查询 EMR / Hologres / MaxCompute 资源与监控 | Describe* / List* 只读查询；压测资源开通属变更，先 preview |
| alibabacloud-emr-cluster-manage | EMR 集群操作 | 已安装 |
