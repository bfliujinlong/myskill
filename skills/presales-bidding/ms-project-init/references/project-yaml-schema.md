# project.yaml 字段契约

`project.yaml` 是当前机会项目的身份和运行变量，不是 Company KB。

## 必填字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | string | 当前为 `0.1.0` |
| `project_id` | string | 业务项目编码 |
| `customer_name` | string | 用户或正式输入确认的客户名称 |
| `opportunity_name` | string | 机会名称 |
| `opportunity_type` | string | v0.1 使用 `new-bidding` |
| `engagement_type` | enum | 四类服务项目类型之一 |
| `stage` | string | 当前项目阶段 |
| `owner` | string | Project/Bid Owner |
| `language` | string | 默认 `zh-CN` |
| `sensitivity` | string | 项目敏感级别 |
| `artifact_status` | enum | 初始化固定为 `working` |
| `selected_offerings` | list[string] | 本项目明确选择的 Offering |

## 可选字段

- `industry`：未确认时写 `unconfirmed`；
- `deadline`：客户或采购方正式截止时间；
- `required_outputs`：明确要求的工件；
- `notes`：不适合结构化字段的已确认说明。

## 约束

1. 客户名、机会名和行业不得从 Workspace 名称或模型常识推断；
2. 客户事实应在项目证据中保留来源；
3. `project.yaml` 不保存密码、Token、联系人隐私或完整客户架构；
4. Agent 初始化后只能写 `working`；
5. 已有 `project.yaml` 不覆盖，修订由 Project Owner 确认。

## 示例

```yaml
schema_version: "0.1.0"
project_id: "SANDBOX-MS-001"
customer_name: "测试客户"
opportunity_name: "Managed Service 测试机会"
opportunity_type: "new-bidding"
engagement_type: "managed-service"
stage: "discovery"
owner: "测试Owner"
industry: "unconfirmed"
language: "zh-CN"
sensitivity: "internal-test"
artifact_status: "working"
selected_offerings:
  - "SmartCare for Cloud"
```
