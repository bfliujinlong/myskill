# 治理与写入边界

## 权限公式

```text
Agent 有效权限
= 当前用户权限
∩ 当前 Skill 授权范围
∩ 当前任务范围
∩ 当前目录和工件状态
```

## 可以执行

- 在目标 Workspace create-if-missing；
- 创建七区骨架、README、`project.yaml` 和初始化报告；
- 按显式 Engagement Type 创建一个动态模块；
- 只读检查 Company KB 是否挂载；
- 输出缺失、跳过、告警和错误。

## 禁止执行

- 写入、复制、移动或删除 Company KB 内容；
- 根据平台环境推断客户身份或行业；
- 跟随业务目录软链接写到 Workspace 外；
- 覆盖已有文件；
- 删除或重命名客户材料；
- 默认建立 POC；
- 自动批准、发布、外发或晋升公司知识；
- 扩大报价、SOW、SLA、RACI、合同和其他履约承诺；
- 输出认证凭证。

## Gate

初始化内部骨架通常是 INFO/WARN。以下情况 BLOCK：

- 项目身份冲突；
- 输入类型不受支持；
- 目标路径越过 Workspace；
- Schema 或模板损坏；
- 请求覆盖已有正式内容；
- 请求将工作稿直接标记为批准或发布。

Company KB 缺失本身只 WARN，因为项目可先搭骨架；但在使用公司能力、报价、SLA或合同知识前必须完成挂载。

## 状态

本 Skill 只产生 `working` 工件。`review`、`approved`、`released`、`superseded`、`archived` 由后续流程和授权角色管理。
