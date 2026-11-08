# adapters/knodo/

- **存放什么**：Knodo 平台的 Skill 适配实现。
- **不存放什么**：Skill 业务源码、测试、客户材料、凭证。
- **权威源**：Knodo 是最终落地、开发与测试平台。

## Company KB 路径适配（RC1-P3-001）

核心 Skill **平台无关**，不硬编码任何 Knodo 挂载路径（如 `pcs-presales`），也不读取平台环境变量。Company KB 路径由**适配层显式注入**。

`company_kb_resolver.py` 是唯一负责解析 Company KB 路径的适配组件：

- 解析顺序（仅显式注入）：
  1. `--company-kb-path` 参数；
  2. `PCS_COMPANY_KB_PATH` 环境变量；
  3. 均无 → `WARN`（可先搭骨架）；使用能力/报价/SLA/合同知识前 → `BLOCK`（`--require` 时 exit 3）。
- Sandbox 适配值可为本环境挂载的 `/shared/pcs-presales`（由适配层注入，不写入核心 Skill）。
- **硬规则**：不扫描 Workspace；不按目录名猜测；不对只读挂载做 touch/write 探测（仅只读 stat 存在性检查）；不虚构默认业务路径。

核心脚本 `ms-project-init/scripts/*.py` 保持平台无关：其 `--company-kb-path` 默认 `_shared/company-knowledge` 为**架构基线的平台无关约定**，非 Knodo 特有路径；脚本不读取任何环境变量（`os.environ` 被治理测试禁止）。原 19 项 ms-project-init 契约测试保持通过。

## 用法

```bash
python3 adapters/knodo/company_kb_resolver.py --company-kb-path /shared/pcs-presales
PCS_COMPANY_KB_PATH=/shared/pcs-presales python3 adapters/knodo/company_kb_resolver.py
python3 adapters/knodo/company_kb_resolver.py --require   # 无注入 -> BLOCK / exit 3
```
