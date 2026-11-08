# Knodo 运行注意事项

## 安装位置

直接上传 Skill 包后，Knodo 文档说明 Skill 存储于 Workspace 的 `.claude/skills/`。标准路径通常为：

```text
.claude/skills/ms-project-init/
```

若由完整 Plugin 挂载，应从当前加载的 `SKILL.md` 实际位置解析 Skill 根目录，不能假设固定 Plugin ID。

## Company KB

路径**由适配器显式注入**，不从目录名硬编码或扫描猜测（见 SKILL.md 步骤 3.5）：

- 解析顺序：`--company-kb-path` 参数 → `PCS_COMPANY_KB_PATH` 环境变量 → 两者皆无则 WARN（骨架可继续），KB-backed 能力（定价/SLA/契约）则 BLOCK；
- 本环境挂载为 `/shared/pcs-presales/`（只读），由 Knodo Template 通过共享链接提供；实际路径以运行时注入值为准；
- 脚本 `--company-kb-path` 的默认值 `_shared/company-knowledge` 只是**平台无关骨架基线**，不是实际挂载判断，不得依赖它判定 Company KB 是否就位；
- 脚本不会创建此目录，也不会复制共享内容。

## Code execution

`scripts/` 需要 Knodo code execution 权限。脚本只使用 Python 3 标准库，不需要安装依赖。

## 环境变量

平台内置 Workspace ID/Name 可以用于审计和排查，但不是客户事实。本 Skill 不读取认证凭证，不打印环境变量，不要求自定义 `JAVIS_` 前缀变量。

## Plugin 生命周期

- 草稿状态适合测试，通常为读写挂载；
- 已发布状态用于稳定版本，通常为只读挂载；
- 状态切换后新开会话再测试；
- 模板的 Plugin 绑定可增量推送；
- 不要用模板目录同步推送项目业务目录，因为目录同步可能删除子空间的项目文件。

## 首次上线顺序

1. 上传到模板 Lab，保持草稿；
2. 新建无客户数据的 Sandbox 子空间；
3. 分别测试 `inspect`、`init`、二次 `init`、`repair`；
4. 验证 Company KB 可读不可写；
5. 验证通过后再发布稳定版本；
6. 真实项目执行需要单独确认。
