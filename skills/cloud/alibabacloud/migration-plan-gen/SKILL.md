---
name: migration-plan-gen
description: "基于 AWS / Azure / Google Cloud 等云厂商的产品规格文档与白皮书，生成针对阿里云的等价或类似解决方案。读取客户提供的源产品规格文档，输出可落地的阿里云架构图、组件清单、限制说明、改造清单。"
description_zh: "跨云迁移方案生成（AWS/Azure/GCP → 阿里云）"
description_en: "Cross-cloud migration plan generation"
version: 1.0.1
agent_created: true
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebSearch
  - WebFetch
  - AskUserQuestion
trigger: ["迁移方案", "跨云迁移", "等价方案", "AWS迁移", "Azure迁移", "GCP迁移", "阿里云方案", "cloud migration"]
---

# 跨云迁移方案生成

把客户在 AWS/Azure/GCP 上用到的产品形态、能力组合，落到阿里云的等价或类似方案上。不是简单产品映射——而是按业务场景给出可落地的架构、组件选型、限制说明、改造清单。

## 输入

-  源云厂商（AWS / Azure / GCP / 自建机房 / 其他云）
-  源产品规格文档（PDF / Word / Markdown / 网页 URL）
-  客户业务场景（SLA 要求、流量量级、合规要求）
-  目标阿里云地域、可用区规划

## 工作流

### 第 1 步 源方案解读

逐份源文档读取，提取：

| 抽取项 | 说明 |
| --- | --- |
| 产品/服务清单 | 每个使用的云服务与版本 |
| 架构拓扑 | VPC、可用区、跨域链路 |
| 关键能力 | 该方案要解决的业务问题 |
| 性能 / SLA | 用户期望的指标 |
| 合规要求 | 数据驻留、加密、审计 |

### 第 2 步 阿里云产品映射

按场景与产品能力映射（不只查表，需结合业务需求选型）：

| 源（AWS） | 阿里云对应 | 选用考量 |
| --- | --- | --- |
| EC2 | ECS | 实例族按计算/内存/存储型选择 |
| RDS | RDS / PolarDB | 是否需要 Oracle 兼容 |
| Aurora | PolarDB | 存算分离、读写分离场景 |
| S3 | OSS | 存储类型按访问频率选 |
| Lambda | 函数计算 FC / SAE | 触发模式与运行时限制 |
| Step Functions | 应用编排服务 / 事件总线 | 复杂流程编排 |
| Kinesis | 消息队列 Kafka / DataHub | 吞吐与延迟 |
| DynamoDB | 表格存储 / Lindorm | 一致性与扩展性 |
| CloudFront | CDN / DCDN | 动静分离与边缘计算 |

### 第 3 步 架构图绘制

产出 Mermaid / drawio 两种格式：

- **目标架构图**：客户视角，含 SLB / API 网关 / 微服务 / 数据库 / 缓存 / 消息 / 存储
- **网络拓扑图**：VPC / VSwitch / 跨域链路 / 安全边界
- **数据流图**：核心业务的请求路径与数据流向

### 第 4 步 差异与限制说明

明确告知客户"哪些能力在阿里云不一样"：

| 差异类别 | 例子 |
| --- | --- |
| 产品不存在 | AWS Ground Station（卫星通信）无直接对应 |
| 能力差异 | Lambda 最大运行时长不同 |
| 计费模型 | 按量 vs 预留 vs Savings Plans |
| 合规差异 | 阿里云全球可用区分布与认证情况 |
| 工具链差异 | 监控（CloudWatch → CloudMonitor）、IaC（CDK → Terraform / ROS） |

### 第 5 步 实施路径

按风险与依赖排序：

```
阶段 1（无依赖，可并行）：
  - 网络与账号规划
  - 监控与日志接入
  - CI/CD 调整

阶段 2（有依赖）：
  - 数据层迁移（参考 oss-migration / rds-migration）
  - 应用层迁移（先无状态，后有状态）
  - 流量切换

阶段 3（优化）：
  - 阿里云原生能力增强（如 SAE / PolarDB）
  - 成本优化（预留实例、存储分层）
```

## 输出交付物

| 文件 | 格式 |
| --- | --- |
| 目标架构图 | Mermaid / drawio + 可选 PNG |
| 组件映射表 | Excel（含阿里云规格 / SKU 选型） |
| 差异说明 | Markdown（产品差异、能力差异、合规差异） |
| 实施路径 | Markdown（阶段、里程碑、依赖） |
| 风险与前提 | Markdown（含验收标准） |

## 边界

- **不做**：实际资源采购与开通（需客户账号授权）。
- **依赖**：源产品规格文档由客户提供，缺失时按"通用最佳实践"给出，需在报告中标注假设。
- **多云混合**：阿里云 + 源云共存的场景需先确认流量走向与数据同步方案。


---

## 输出模板

所有交付物模板见 `references/templates.md`。产出文档时按模板填充，不自创结构；模板未覆盖的字段按项目实际补充并在交付物中注明。

## 可调用能力

执行过程中按需调用以下已安装能力，不要凭记忆硬写命令：

| 能力 | 用途 | 调用说明 |
| --- | --- | --- |
| alibabacloud-migration-mas-product-mapping | 源云→阿里云产品映射（MAS） | 已安装；组件映射表优先以它为准 |
| aliyun-cli skill | 查询目标产品规格、可用区、配额 | 只用 Describe* / List* 只读查询 |
| WebSearch / WebFetch | 拉取源云与阿里云产品文档 | 规格比对时使用，注明文档版本与日期 |
| find-skills skill | 缺专项能力时检索安装 | 本地市场优先 |
