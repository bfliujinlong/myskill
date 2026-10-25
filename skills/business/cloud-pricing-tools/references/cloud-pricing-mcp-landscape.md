# 云厂商 MCP 服务器可用性调研（2026-09-02）

## 各云 MCP 服务器状态

| 云厂商 | MCP 包名 | 状态 | 说明 |
|---|---|---|---|
| AWS | `awslabs.aws-pricing-mcp-server` | ✅ 可用 | 已接入 config.yaml，可查 18+ 服务价格 |
| Azure | `azure-mcp-server` (0.1.0) | ❌ 不可用 | 包存在但无实际可运行的 server 入口 |
| GCP | `gcp-mcp` (0.1.0) | ❌ 不可用 | MCP v1→v2 不兼容，`fastmcp` 找不到 |
| Google Cloud | `google-cloud-mcp` (1.0.0) | ❌ 不可用 | 同上，MCP v2 兼容问题 |
| Azure DevOps | `azure-devops-mcp` (0.2.0) | ❌ 已损坏 | f-string 语法错误，无法运行 |
| 阿里云 | 无 MCP 包 | ❌ 不存在 | PyPI 上无相关包 |
| 腾讯云 | 无 MCP 包 | ❌ 不存在 | PyPI 上无相关包 |
| 华为云 | 无 MCP 包 | ❌ 不存在 | PyPI 上无相关包 |
| 火山引擎 | 无 MCP 包 | ❌ 不存在 | PyPI 上无相关包 |
| OCI | 无 MCP 包 | ❌ 不存在 | PyPI 上无相关包 |

## AWS Pricing MCP 配置

```yaml
mcp_servers:
  awslabs.aws-pricing-mcp-server:
    command: uvx
    args: [awslabs.aws-pricing-mcp-server@latest]
    env:
      FASTMCP_LOG_LEVEL: ERROR
      AWS_PROFILE: default
      AWS_REGION: us-east-1
    disabled: false
```

**调用方式：**
```bash
uvx awslabs.aws-pricing-mcp-server@latest --service AWSEC2 --region us-east-1
```

**已验证可查的服务（18个）：**
AWSLambda, AWSEC2, AWSRDS, AWSS3, AWSVPC, AWSEKS, AWSR53, AWSIAM, AWSCloudWatch, AWSEBS, AWSNATGateway, AWSALB, AWSKinesis, AWSDynamoDB, AWSGlue, AWSSageMaker, AWSWAF, AWSAutoScaling

## 其他云的替代方案

### 中期可补强的 CLI 查价方案
- **阿里云**：`aliyun` CLI 可查部分产品价格
- **腾讯云**：`tcloud` CLI 可查部分产品价格
- **华为云**：`hcloud` CLI 可查部分产品价格
- **GCP**：`gcloud` CLI 可查部分产品价格
- **Azure**：`az` CLI 可查部分产品价格

### 长期方案
- 等待各云官方发布 MCP 服务器
- 或自建 API 代理封装各云定价 API

## 售前报价自动化工作流

### 当前可行方案
1. **AWS**：通过 MCP 自动查真实价格
2. **其他 7 朵云**：靠能力矩阵 + 公开报价做估算对比
3. **售前 Skill 标注**：明确区分"实时查价"与"估算参考"

### 能力矩阵参考
已有一份 `8cloud capability matrix.xlsx`，包含：
- 架构设计能力
- Landing Zone / 账号治理
- DR 容灾方案
- IaC 工具链
- 安全合规
- 网络互联

评分标准：5=完善, 4=较好, 3=中等, 2=有限, 1=缺失

### 报价输出格式
```
[客户画像]：行业/地域/合规要求
[推荐云]：主推/次选/备选 + 理由
[价格对比表]：各云核心服务价格对比
[风险提示]：价格变动、合规差异等
```

## 坑
- `hermes config set` 会把点号当成层级分隔符，导致 `awslabs.aws-pricing-mcp-server` 被嵌套成 `awslabs > aws-pricing-mcp-server`，需手动修复
- `uvx` 需要 `UV_CACHE_DIR` 目录存在且可写，否则报 `Failed to initialize cache`
- 其他云的 MCP 包即使 pip 能装上，也可能因为 MCP SDK 版本不兼容而无法运行
