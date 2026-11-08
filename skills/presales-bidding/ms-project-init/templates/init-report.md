# Workspace 初始化报告

- 项目编码：`{project_id}`
- 机会名称：{opportunity_name}
- 服务类型：`{engagement_type}`
- 初始阶段：`{stage}`
- 初始状态：`working`
- 初始化器：`ms-project-init v0.1`

## 已执行

- 创建七个一级业务区及其二级骨架；
- 为全部骨架目录生成 README 使用契约；
- 按服务类型创建对应动态模块；
- 生成根 README 与 `project.yaml`；
- 采用 create-if-missing，不覆盖已有内容。

## 需人工或验证器确认

- Company KB 已注入路径（本环境 `/shared/pcs-presales/`）且可读不可写；
- 项目变量、成员、权限和敏感级别准确；
- 当前服务类型与机会事实一致。
