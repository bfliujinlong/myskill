# 适配点清单（脚手架型特例）— ms-project-init / references/adaptation-points.md

> **定位**：project-init 是**脚手架型** skill，与其余 7 个"内容生成型"skill 的四文件范式**不同**：
> 它不产出可读工件，而是按 schema 创建目录骨架。因此它**没有 output-template.md**（框架即 `workspace-schema.json`），
> 也**没有内容层适配**——七区骨架对任何客户、任何项目**完全一致，零适配**。
>
> 它的**唯一适配点**是：按 `engagement_type` 从 schema 的 `engagement_modules` 中**选择性创建一个**项目类型模块。
> 除此之外，骨架结构不随客户变化。

---

## 为什么 project-init 不套用标准 output-template 范式

| 维度 | 内容生成型 skill（其余 7 个） | project-init（脚手架型） |
|------|------------------------------|--------------------------|
| 产出 | 可读文本工件（方案/报价/SOW…） | 目录骨架 + project.yaml + 初始化报告 |
| 框架载体 | `output-template.md` | `workspace-schema.json`（27KB 结构定义） |
| 内容适配 | 多适配点（周期/规模/费率/叙事…） | **无**——七区骨架固定 |
| 唯一可变点 | — | `engagement_type` 决定装配哪个模块 |
| 实例参考 | reference-example 示范一种填法 | reference-example 示范一次装配结果 |

> 结论：强行给 project-init 套 output-template 会制造伪框架。正确做法是**保留 schema references 作为框架层**，仅补齐"唯一适配点"说明与一次装配示范。

---

## 唯一适配点：engagement_type 模块选择

| 适配点 | 取值来源 | 档位（schema `engagement_modules` 键） | 装配结果 |
|--------|---------|------------------------------------------|----------|
| `engagement_type` | `project.yaml` 显式字段（不推断） | `managed-service` | 装配 Managed-Service 6 目录（服务范围/运营治理/SLA/Mobilization/持续改进…） |
|  |  | `build-implementation` | 装配 Build-Implementation 6 目录（架构/实施迁移/计划/测试验收/移交…） |
|  |  | `consulting-assessment` | 装配 Consulting-Assessment 6 目录（目标范围/评估方法/证据发现/建议/蓝图…） |
|  |  | `hybrid-integration` | 装配 Hybrid-Integration 5 目录（Build/Transition/Operation/跨阶段衔接…） |

> 模块内容全部由 `workspace-schema.json` 的 `engagement_modules` 定义，本 skill 不新增、不改写目录含义。

---

## 选档纪律（普适，不变）

1. **engagement_type 必须显式**：来自 `project.yaml`，**严禁**从 Workspace 名/环境变量/模型常识推断。
2. **只装一个模块**：按显式 engagement_type 只创建对应一个项目类型模块，不创建无关空模块。
3. **七区骨架零适配**：`01_客户输入` ~ `07_...` 七区结构对任何项目完全一致，不因客户变化。
4. **create-if-missing**：只创建缺失目录/文件，**绝不覆盖**已有内容。
5. **治理边界不参与适配**：`governance-boundaries.md` 的写入禁令（不写 KB/不推断身份/不扩大承诺）对任何项目不可调。
6. **hybrid 不是拼接**：hybrid-integration 装配的是含"跨阶段责任与商业衔接"的完整模块，不是简单堆叠 build+managed。

---

## 与其余 references 的关系

- 框架层（不变）：`workspace-schema.json` + `project-yaml-schema.md` + `governance-boundaries.md` + `knodo-runtime-notes.md`；
- 唯一适配点：本文件（engagement_type 四值模块选择）；
- 装配示范：`reference-example.md`（reference-only，一次装配长什么样）。
