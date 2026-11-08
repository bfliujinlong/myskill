# 授权领取清单（只要 2 朵，照抄即可）

生成时间：2026-11-01 · 现状 **6/8 已可读数**，只差腾讯云 + 火山引擎

---

## 你要做的事（一共 2 件，各 5 分钟）

### □ 第 1 件：腾讯云 SecretId / SecretKey

1. 打开 https://console.cloud.tencent.com/cam/capi
2. **新建子用户**（不要主账号）→ 只勾「编程访问」，**不开控制台登录**
3. 授权方式选「自定义策略 → 按策略语法创建」，贴：

```json
{
  "version": "2.0",
  "statement": [{
    "effect": "allow",
    "action": [
      "cvm:InquiryPriceRunInstances",
      "cvm:DescribeZoneInstanceConfigInfos",
      "cvm:DescribeInstanceTypeConfigs",
      "cvm:DescribeRegions"
    ],
    "resource": "*"
  }]
}
```

4. 拿到 `SecretId` + `SecretKey`，**两种方式给我**（选一）：

```bash
# A. 环境变量（推荐，不落盘）
export TENCENTCLOUD_SECRET_ID="AKIDxxxx"
export TENCENTCLOUD_SECRET_KEY="xxxx"

# B. 落文件（我会 chmod 600）
mkdir -p ~/.tencentcloud && cat > ~/.tencentcloud/credentials <<'EOF'
[default]
secret_id = AKIDxxxx
secret_key = xxxx
EOF
chmod 600 ~/.tencentcloud/credentials
```

全部是**只读询价** action，不创建/不删除/不花钱。

---

### □ 第 2 件：火山引擎 AccessKey / SecretKey

1. 打开 https://console.volcengine.com/iam/keymanage/
2. **建子账号**再建密钥（别用主账号）
3. 自定义策略，贴：

```json
{
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "billing:QueryPriceForPayAsYouGo",
      "ecs:DescribeInstanceTypes",
      "ecs:DescribeInstancesOperationCount"
    ],
    "Resource": "*"
  }]
}
```

4. 拿到 AK / SK，两种方式给我（选一）：

```bash
# A. 环境变量（推荐）
export VOLCENGINE_ACCESS_KEY="AKxxxx"
export VOLCENGINE_SECRET_KEY="xxxx"

# B. 落文件
mkdir -p ~/.volcengine && cat > ~/.volcengine/config.json <<'EOF'
{"current":"default","profiles":{"default":{
  "mode":"AK","access-key":"AKxxxx","secret-key":"xxxx","region":"cn-beijing"}}}
EOF
chmod 600 ~/.volcengine/config.json
```

---

## 更安全的替代：STS 临时令牌（可选）

不想给长期 AK 就用这个，有时效、泄露损失小：

- **腾讯云**：CAM → 角色 → `sts:AssumeRole` → 拿 `TmpSecretId/TmpSecretKey/Token` 三元组
  → 我这边 `credential.Credential(id, key, token)` 多传一个 token 即可（代码已写好分支）
- **火山引擎**：IAM → 角色 → 扮演 → 拿 `AK/SK/SessionToken`
  → SDK 直接吃 `VOLCENGINE_SESSION_TOKEN` 环境变量，**零改代码**

两种我都已支持，你给哪种我都能接。

---

## 剩下 6 朵：你什么都不用做

| 云 | 状态 | 凭据 |
|---|---|---|
| OCI | ✅ READY | 无需（官方匿名价目 API） |
| 华为云 | ✅ READY | 无需（价格计算器匿名接口） |
| Azure | ✅ READY | 无需（官方 Retail Prices API） |
| AWS | ✅ READY | 无需（Pricing Calculator 静态端点） |
| GCP | ✅ READY | 无需（第三方聚合，已在报告披露） |
| 阿里云 | ✅ READY | 已有 AK 在跑 |

**AWS 那个 `awslabs.aws-pricing-mcp-server` 不用装、AK 不用给** —— AWS 已匿名可读，装了反而多一份密钥风险。

---

## 我不做的事（红线）

- 凭据一律 `chmod 600`，只落 `$HOME`
- **绝不**写进 skill 文件 / `clouds.yaml` / git / 任何文档
- **绝不**出现在聊天、Telegram、发布文档里
- 只跑询价，**不创建任何资源**，零费用

## 我已经提前做好的（你给凭据前就位）

- **SDK 已预装**到 `~/.hermes/cloud-mcp-venvs/pricebench`（18 MB），`bench.py` 自动识别加载
  → 你给凭据后**不需要等装包**，直接能跑
- **火山 import 名已取证修正**：拆 wheel 确认 API 类真名是 `BILLINGApi`（不是 `BillingService`），
  方法 `query_price_for_pay_as_you_go(body)`，`count` 是字符串、`quantity` 是整数 —— 已按真实签名改好
- **腾讯云镜像不再硬编码**：原占位 `img-l8og963d` 会随地域/下线失效，改为 `DescribeImages` 动态取公共 Linux 镜像
- 两个 adapter 无凭据时会**明确报 CredentialError + 指引**，不静默返回空价

## 你给我之后我会做什么

1. 实调验证（预计 5 分钟，SDK 已装好）→ 2. `clouds.yaml` 改 READY → 3. 校准 4 档机型对齐口径
→ 4. `compare --shape all` 八朵同表 → 5. 更新 SKILL/README → 6. 重生成全景 HTML → 7. TG 发你

**已知不确定项（会如实告诉你，不装成功）**：火山 `QueryPriceForPayAsYouGo` 的
`configuration_code` / `charge_item_code` 枚举值，没有 AK 无法预先确认。
首次实调若枚举对不上，我会用 `DescribeInstanceTypes` 校准；
实在不通就退化为「控制台询价页手工录入 + 标注日期」，**不会假装自动化成功**。
