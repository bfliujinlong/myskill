---
name: ms-project-init
description: >
  为安畅服务型 New Bidding 创建、检查或安全修复标准项目 Workspace（七区骨架 + project.yaml），只创建缺失容器不填造业务内容。
  使用当用户说"初始化项目"、"新建 Workspace"、"项目骨架"、"检查项目结构"、"补齐目录"、"project init"时激活。
version: 0.1.0-rc.10
keywords:
  - 安畅售前
  - New Bidding
  - Workspace初始化
  - project-init
  - Managed Service
---

# PCS Project Init

## Overview

本 Skill 为安畅服务型 New Bidding 创建确定性的项目骨架。它严格区分只读 Company KB 与项目变量，只创建必要容器和 README，不填造业务内容。

核心原则：

> 显式项目事实 → 先校验 → 只在当前 Workspace create-if-missing → 只推进到 working。

## When to Use

使用场景：

- 新机会从 Knodo Template 创建后初始化 Workspace；
- 检查现有项目是否符合七区骨架；
- 安全补齐缺失目录或 README；
- 评估旧项目迁移差异。

不要用于：

- 修改或复制 Company KB；
- 自动迁移现有项目；
- 创建产品型 POC 流程；
- 生成 RFP、方案、报价或合同内容；
- 批准、发布或对外发送工件。

## Prerequisites

1. 当前目录是目标 Workspace 根目录；
2. Knodo Template 已将 Company KB 挂载（本环境为 `/shared/pcs-presales/`），由适配器/环境变量显式注入路径；脚本 `--company-kb-path` 的默认值只是平台无关基线，不作为实际挂载判断；
3. 用户已提供或确认项目变量；
4. Python 3 可用；
5. 执行脚本时启用 Knodo code execution 权限。

Company KB 缺失时允许初始化，但必须 WARN；不得创建一个同名普通目录冒充挂载。

## Modes

| Mode | 行为 | 写入 |
|---|---|---|
| `init` | 新建根文件、七区骨架、README 和项目类型模块 | 仅 create-if-missing |
| `inspect` | 检查根文件、骨架、动态模块和 Company KB | 无 |
| `repair` | 补齐缺失项 | 仅 create-if-missing |
| `migrate` | 评估旧项目迁移 | v0.1 不执行；只生成计划并等待确认 |

## Required Inputs

初始化前逐项确认：

```json
{
  "project_id": "",
  "customer_name": "",
  "opportunity_name": "",
  "opportunity_type": "new-bidding",
  "engagement_type": "managed-service",
  "stage": "discovery",
  "owner": "",
  "selected_offerings": [],
  "language": "zh-CN",
  "sensitivity": ""
}
```

可选：`industry`。未确认时保持 `unconfirmed`，不得推断。

允许的 `engagement_type`：

- `managed-service`
- `build-implementation`
- `consulting-assessment`
- `hybrid-integration`

项目和客户身份必须来自用户或正式项目输入。平台 Workspace 名称只能用于平台审计，不是客户事实。

完整字段见 `references/project-yaml-schema.md`。

## Write Boundary

有效写入范围：

```text
当前 Workspace 根目录
├── README.md
├── project.yaml
├── 00_项目管理/
├── 01_客户输入/
├── 02_机会与策略/
├── 03_方案与应答/
├── 04_商务与合同/
├── 05_评审与发布/
└── 06_移交与复盘/
```

禁止：

- 写入 Company KB（本环境为 `/shared/pcs-presales/`）；
- 跟随业务目录软链接写到 Workspace 外；
- 覆盖任何已有文件；
- 删除、重命名或移动客户材料；
- 自动创建与当前项目类型无关的模块；
- 自动创建 POC；
- 将状态写为 `approved` 或 `released`；
- 输出平台内置认证凭证。

详细边界见 `references/governance-boundaries.md`。

## Workflow: init

### 1. 收集并回显变量

只回显业务字段，不输出环境变量或凭证。将事实、假设和未确认项分开。

### 2. 展示执行范围

执行前说明：

- 将创建七个一级业务区及全部 README；
- 将按 `engagement_type` 创建一个动态模块；
- 已有文件全部跳过；
- Company KB 只检查、不创建、不复制；
- 状态停留在 `working`。

用户已明确要求初始化时可继续；若输入存在冲突，先停止并确认。

### 3. 准备输入 JSON

基于已确认变量创建临时 JSON。不要把密码、Token 或客户原始材料写入该文件。

### 3.5 Knodo 适配入口：解析 Company KB 路径（强制先于执行）

核心 `init_workspace.py` 平台无关，不猜测 Company KB 路径。在 Plugin 运行时，先调用 Knodo 适配层解析显式注入的路径（`--company-kb-path` 或 `PCS_COMPANY_KB_PATH`），把解析结果 `path` 作为 `--company-kb-path` 传给核心脚本：

```bash
# Plugin 运行时，适配器与 skills/ 同级，位于 plugin 根 adapters/knodo/
KB_JSON=$(python3 "$PLUGIN_ROOT/adapters/knodo/company_kb_resolver.py" \
  --company-kb-path "${COMPANY_KB_PATH:-}")
KB_PATH=$(printf '%s' "$KB_JSON" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['path'] or '')")
# 未注入 -> KB_PATH 为空；适配器输出 WARN/BLOCK；不回退硬编码默认，不扫描、不猜测。
```

`$PLUGIN_ROOT` 从当前已加载 `SKILL.md` 的真实位置上溯到 plugin 根（含 `.claude-plugin/`、`skills/`、`adapters/`），不得猜测其他项目路径。

### 4. 执行

执行（`--company-kb-path` 取适配器解析结果 `$KB_PATH`；为空则由适配器 WARN/BLOCK 决定是否继续）：

```bash
python3 "$PLUGIN_ROOT/skills/ms-project-init/scripts/init_workspace.py" \
  --mode init \
  --workspace "$PWD" \
  --config /path/to/confirmed-project-input.json \
  --company-kb-path "$KB_PATH"
```

核心脚本仍平台无关：不读环境变量、不硬编码 Knodo 路径（如 `pcs-presales`）。路径始终由适配器显式注入。

### 5. 验证

```bash
python3 "$PLUGIN_ROOT/skills/ms-project-init/scripts/validate_workspace.py" \
  --workspace "$PWD" \
  --engagement-type managed-service \
  --company-kb-path "$KB_PATH"
```

当适配器解析出有效路径时，`inspect`/`validate` 使用该路径检查挂载；路径正确挂载后不再输出旧默认路径的 WARN。

将 `managed-service` 替换为实际项目类型。

### 6. 报告

向用户报告：

- `created`
- `skipped`
- `warnings`
- `errors`
- Company KB 挂载状态
- `project.yaml` 关键字段
- 下一项仍需人工确认的内容

不要把“结构生成成功”表述为“项目内容已就绪”。

## Workflow: inspect

```bash
python3 .claude/skills/ms-project-init/scripts/init_workspace.py \
  --mode inspect \
  --workspace "$PWD" \
  --company-kb-path "$KB_PATH"
```

要求：

- 不创建、修改或删除任何文件；
- 缺失骨架返回非零；
- 仅 Company KB 缺失时可以返回 WARN；
- 输出缺失项和风险。

> Company KB 路径必须由适配器解析结果注入（见 3.5 步），不要写作 `_shared/company-knowledge/` 这类非基线常值。

## Workflow: repair

先运行 `inspect`，向用户展示差异。用户明确要求补齐后执行：

```bash
python3 .claude/skills/ms-project-init/scripts/init_workspace.py \
  --mode repair \
  --workspace "$PWD" \
  --config /path/to/confirmed-project-input.json
```

`repair` 只能补齐缺失项；如果现有内容与 Schema 冲突，保留原内容并报告，不得自动覆盖。

## Workflow: migrate

v0.1 不自动迁移。遇到旧项目时：

1. 运行 `inspect`；
2. 建立原目录、目标目录和冲突清单；
3. 标记原始材料、工作稿、正式版本和共享知识；
4. 给出迁移、保留、链接、跳过建议；
5. 等待用户逐项确认；
6. 不调用 `init` 或 `repair` 伪装成迁移完成。

## Failure Handling

| 情况 | 行为 |
|---|---|
| 必填字段缺失 | 退出，不写入 |
| Engagement Type 不支持 | 退出，不写入 |
| 业务目录软链接到 Workspace 外 | BLOCK |
| Company KB 未挂载 | WARN，不创建假目录 |
| 已有文件 | SKIP，不覆盖 |
| Schema 或模板损坏 | 退出并报告具体文件 |
| 验证器发现缺失 | 保持项目可见，不能声称初始化完整 |

## Acceptance Checklist

- [ ] 七个一级业务区存在；
- [ ] 全部基础和动态目录都有 README；
- [ ] 只创建当前 Engagement Type 模块；
- [ ] 根 README、`project.yaml` 和初始化报告存在；
- [ ] 二次执行不覆盖已有内容；
- [ ] Company KB 未被复制或写入；
- [ ] 无默认 POC；
- [ ] 工件状态为 `working`；
- [ ] 验证器无 missing/errors；
- [ ] WARN 已向用户显性说明。

## References

- `references/workspace-schema.json`：唯一机器目录源；
- `references/project-yaml-schema.md`：项目变量契约；
- `references/governance-boundaries.md`：权限与硬边界；
- `references/knodo-runtime-notes.md`：Knodo 挂载和运行注意事项；
- `examples/`：四类项目的无敏感测试输入。
