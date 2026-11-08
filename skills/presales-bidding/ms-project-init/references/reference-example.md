# 参考实例：示例 Managed Service 项目（reference-only）— ms-project-init / references/reference-example.md

> ⚠️ **本文件是参考实例，不是模板，不得照抄。**
> 这是一个**脱敏的示例项目**——用于示范 `workspace-schema.json` 的七区骨架 + `engagement_modules` 装配机制如何成立。
> 下列是该示例项目一次初始化**在唯一适配点（engagement_type）上的选择结果**，仅供"一次装配长什么样"的参照。
> 新项目**必须**按自己 `project.yaml` 的 engagement_type 重新装配，**不能**默认套用示例选择。

---

## 示例项目在唯一适配点的选择结果

| 项 | 示例取值 | 依据 |
|----|---------|------|
| `engagement_type` | `managed-service` | 该项目采购持续托管运维 |
| 装配的项目类型模块 | `03_方案与应答/01_服务方案/02_项目类型模块/Managed-Service/` | 按 engagement_type 从 schema 选装 |
| 七区骨架 | 与任何项目**完全相同**（零适配） | 骨架不因客户变化 |

装配出的 Managed-Service 子目录（来自 schema，非本项目新增）：
- 服务范围与目录 / 运营组织与治理 / SLA与运营保障 / Mobilization与服务接管 / 持续改进与AI-driven

---

## 示例 project.yaml 关键字段（脱敏骨架，仅示范字段形态）

```yaml
customer_name: "（客户名，来自正式输入，不推断）"
opportunity_type: "new-bidding"
engagement_type: "managed-service"    # ← 唯一驱动模块装配的字段
artifact_status: "working"            # 初始化只到 working
industry: "unconfirmed"               # 未确认即写 unconfirmed，不臆测
```

> 业务数量（如云主机/中间件/K8s 台套数）**不属于 project-init 范畴**，
> 它们是下游 rfp-analyze / pricing / sow 阶段的内容，初始化阶段不落任何业务数量。

---

## ⚠️ 脚手架保真示范（关键纪律）

- **engagement_type 显式驱动**：装 managed-service 是因为 project.yaml 明确写了，**不是**从客户名字推断；换客户若写 build-implementation 就装 Build 模块；
- **只装一个模块**：只创建 Managed-Service，不顺手创建 Build/Consulting/Hybrid 空模块；
- **create-if-missing**：二次 init 目录时，已存在的目录**跳过不覆盖**，只补缺失；
- **不写 KB / 不推断身份**：初始化不读取也不写入 Company KB，客户身份仅来自 project.yaml。

---

## 使用边界

- 本文件 reference-only，随框架发布但**不参与运行时装配**；
- skill 运行时**默认不加载本文件**，仅在需要"装配示范"时按需参照；
- 示例的 managed-service 选择不得作为任何新项目的默认；
- 本文件已为脱敏骨架，无客户机密内容。
