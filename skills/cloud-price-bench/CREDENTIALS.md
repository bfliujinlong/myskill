# 8 云统一比价 · 凭据授权指南（2026-11-01 实测版）

> 目标：**8 朵云一个入口比价**。现状 **6/8 已自配可读数**，需你出手的只有 **2 朵**。
> 本文回答三个问题：① 哪朵要登录、怎么授权 ② 除了 AK 还有没有别的路 ③ 我拿到之后干什么。

## 0. 一句话结论

| 你要做的 | 数量 |
|---|---|
| 现在就要给凭据 | **2 朵**：腾讯云、火山引擎 |
| 完全不用管（我已自配，匿名可读） | **5 朵**：OCI、华为云、Azure、AWS、GCP |
| 已有凭据在跑 | **1 朵**：阿里云（可选后续换 RAM 只读） |
| AWS AK | **不要给**，那个 MCP 也不用装（见 §4） |

---

## 0.1 「不限于 AK，最好你自己配好」——我已经配了 5 朵零凭据

这 5 朵**不需要任何账号/密钥**，靠官方公开端点取价，我全部实测调通：

| 云 | 用的通道 | 性质 |
|---|---|---|
| OCI | 官方 Price List API | 官方公开，668 SKU |
| 华为云 | 价格计算器 `productInfo` 接口 | 官方公开，intl 站 USD 直读 |
| Azure | 官方 Retail Prices API | 官方公开，微软明文免鉴权 |
| AWS | Pricing Calculator 静态端点 | 官方公开 |
| GCP | 机型/价格聚合页 | **第三方**（非 Google 官方），已在报告披露 |

剩下 3 朵里，阿里云你早就给了 AK；腾讯云/火山**匿名通道我全试过了（11+ 条路径）全堵**，
这两朵的厂商设计就是「询价必须带身份」，没有绕过办法（详见 §2.4 / §3.4）。

### 0.2 怎么验证我没在吹（三条命令自查）

```bash
# 1) 看每朵云的接入状态（status 列 = READY 就是现在真能取价）
python3 ~/.hermes/skills/cloud-price-bench/bench.py status

# 2) 跑一次六云同表比价
python3 ~/.hermes/skills/cloud-price-bench/bench.py compare --shape all

# 3) 看单朵云的实测证据（含 verified 字段：某机型 = 某价 @ 某日期）
grep -n "verified" ~/.hermes/skills/cloud-price-bench/clouds.yaml
```

`clouds.yaml` 里每朵都有 `verified:` 字段，形如 `2026-10-31 t3.micro=$0.0104/hr` ——
**这是实调留痕，不是文档抄来的**。目前 6 朵均有该字段，腾讯云/火山为 `NEED_CRED` 无。

---


> 目标：统一比价。**8 朵里 6 朵已经我自己配好、能跑**，只有 **腾讯云 / 火山引擎** 两朵必须你给凭据。
> 下面写清：去哪拿、最小权限给什么、文件放哪、怎么验。

## 一、现状总览（8 朵）

| # | 云 | 状态 | 是否要你出手 | 取价方式 |
|---|---|---|---|---|
| 1 | OCI | ✅ READY | 否 | 官方价目 API，完全匿名 |
| 2 | GCP | ✅ READY | 否 | 匿名机型页（第三方聚合站，已在 SKILL.md 披露） |
| 3 | 华为云 | ✅ READY | 否 | 价格计算器 productInfo 接口，匿名 |
| 4 | Azure | ✅ READY | 否 | 官方 Retail Prices API，匿名 |
| 5 | AWS | ✅ READY | 否 | Pricing Calculator 静态端点，匿名 |
| 6 | 阿里云 | ✅ READY | 否（已有 AK） | ECS DescribePrice |
| 7 | **腾讯云** | ⛔ NEED_CRED | **是** | CVM `InquiryPriceRunInstances` |
| 8 | **火山引擎** | ⛔ NEED_CRED | **是** | Billing `QueryPriceForPayAsYouGo` |

**结论：你只需要去搞 2 个 —— 腾讯云 SecretId/SecretKey、火山引擎 AccessKey/SecretKey。**

---

## 二、腾讯云（CVM 询价）

### 1. 去哪拿
- 控制台 → 访问管理 CAM → 密钥管理：https://console.cloud.tencent.com/cam/capi
- **必须建「子用户」**，不要用主账号密钥（主账号 AK 泄露 = 全账号沦陷）
- 子用户创建时勾选「编程访问」即可，**不要开控制台登录**

### 2. 最小权限（推荐自定义策略，别用预设）
预设策略名 `QcloudCVMReadOnlyAccess` 我**没能从 SDK/文档确认到**（文档页是 JS 渲染，抓不到）→ 直接在控制台「新建自定义策略 → 按策略语法创建」，贴下面这段（已确认这几个 action 真实存在于 `tencentcloud-sdk-python-cvm` 3.1.178）：

```json
{
  "version": "2.0",
  "statement": [
    {
      "effect": "allow",
      "action": [
        "cvm:InquiryPriceRunInstances",
        "cvm:DescribeZoneInstanceConfigInfos",
        "cvm:DescribeInstanceTypeConfigs",
        "cvm:DescribeRegions"
      ],
      "resource": "*"
    }
  ]
}
```

全是**只读询价**，不创建、不删除、不花钱。

### 3. 文件放哪
```
~/.tencentcloud/credentials      （ini 格式，chmod 600）
```
```ini
[default]
secret_id = AKIDxxxxxxxxxxxxxxxx
secret_key = xxxxxxxxxxxxxxxxxxxx
```
或走环境变量：`TENCENTCLOUD_SECRET_ID` / `TENCENTCLOUD_SECRET_KEY`（SDK 的 `DefaultCredentialProvider` 先读环境变量再读文件，两者都认）。

### 4. 我会怎么用
`InquiryPriceRunInstances`，`InstanceChargeType=POSTPAID_BY_HOUR`（按量后付费），
返回 `ItemPrice.UnitPrice` = **元/小时**，这就是真·On-Demand 单价，跟其他 7 朵口径一致。
机型列表用 `DescribeZoneInstanceConfigInfos`（返回 CPU/内存/机型/售卖状态）。

---

## 三、火山引擎（ECS 按需询价）

### 1. 去哪拿
- 控制台 → 访问控制 IAM → 密钥管理：https://console.volcengine.com/iam/keymanage/
- **建子账号**再建密钥，别用主账号
- 拿到的两个值：Access Key ID / Secret Access Key

### 2. 最小权限
自定义策略，只给这两个 action（已从 `volcenginesdk-ecs` / `volcenginesdk-billing` 5.0.56 包里确认存在）：

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "billing:QueryPriceForPayAsYouGo",
        "ecs:DescribeInstanceTypes",
        "ecs:DescribeInstancesOperationCount"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. 文件放哪
```
~/.volcengine/config.json        （json 格式，chmod 600）
```
```json
{
  "current": "default",
  "profiles": {
    "default": {
      "mode": "AK",
      "access-key": "AKxxxxxxxxxx",
      "secret-key": "xxxxxxxxxxxx",
      "region": "cn-beijing"
    }
  }
}
```
或环境变量：`VOLCENGINE_ACCESS_KEY` / `VOLCENGINE_SECRET_KEY`（SDK 默认链第一步就是读这两个）。
（SDK 凭据链：环境变量 → OIDC → `~/.volcengine/config.json` → ECS 实例角色）

### 4. 一个诚实的提醒
`QueryPriceForPayAsYouGo` 这个**按需询价接口确实存在**（在 `volcenginesdk-billing` 里，之前按 `DescribePrice/InquiryPrice` 命名习惯 grep 漏掉了）。但它要传 `product` + `config_list[]`（含 `configuration_code` / `charge_item_code` / `count` / `use_duration`），**这些枚举值我拿不到 AK 就无法确认**。
所以：AK 给我之后，我会先用 `ecs:DescribeInstanceTypes` 拿机型规格、再实调询价接口试参数。如果枚举值对不上，火山这朵可能退化为「控制台询价页手工录入 + 标注日期」，我不会假装自动化成功。

---

## 四、AWS：不用给 AK，也别装那个 MCP

你之前贴的 `awslabs.aws-pricing-mcp-server` **没有 AK 不能用**（实测三重确认：必须 `AWS_PROFILE` 指向有效凭据，匿名直接失败）。
但**对我们目标零增量** —— AWS 已经匿名 READY 了（Pricing Calculator 静态端点，t3.medium=$0.0416/hr 已验证）。
建议：**跳过这个 MCP，不给 AWS AK**，少一份密钥就少一份风险。
如果哪天要 AWS 的 RI/SP 折扣价（匿名拿不到），再单独谈。

---

## 五、可选加固：阿里云 AK

`~/.aliyun/config.json` 里现在是既有 AK（profile default，cn-hangzhou），能跑。
**建议后续换成 RAM 只读子用户**（授权 `AliyunECSReadOnlyAccess`），跟上面腾讯/火山一个标准。不急，等你顺手时换。

---

## 六、安全红线（我这边会严格执行）

- 凭据文件一律 `chmod 600`，只落 `$HOME` 下
- **绝不**写进 skill 文件、`clouds.yaml`、git、任何文档
- **绝不**在聊天 / Telegram / 发布文档里出现明文 Key
- 只给询价只读权限，**不开任何写/删/购买权限**，零费用
- 拿到之后我只跑询价，不创建任何资源

---

## 七、你给我之后我会做什么

1. 建 `adapters/tencent.py` / `adapters/volcengine.py`，装 SDK 到 `~/.hermes/cloud-mcp-venvs/{tencent,volcengine}`
2. 实测调通 → `clouds.yaml` 里把这两朵改成 `READY`
3. 校准 4 档机型（2c4g / 2c8g / 4c16g / 8c32g）对齐口径
4. `bench.py compare --shape all` → 8 朵同表
5. 更新 `SKILL.md` / `team-ops/README.md` / `ONBOARDING.md`
6. 重新生成全景 HTML → Telegram 发你


---

## 八、附：除了 AK 还有哪些路（你要「不限于 AK」，这是全清单）

按「我能自己搞定 → 要你点一下 → 要你去控制台」排序：

| 方式 | 适用 | 我能否自助 | 说明 |
|---|---|---|---|
| 官方匿名价格 API | OCI / Azure | ✅ 已完成 | 厂商明文免鉴权，最优 |
| 价格计算器公开接口 | 华为云 / AWS | ✅ 已完成 | 网页计算器后端接口，匿名可调 |
| 第三方聚合价 | GCP | ✅ 已完成 | 已在报告标注非官方，GCP 官方通道全 403 |
| 环境变量注入 | 全部 | ✅ 你给我值即可 | 比落文件更安全，不进磁盘 |
| **实例角色 / OIDC** | 腾讯云 TKE、火山 ECS | ⚠️ 不适用 | 需要跑在对方云上的机器里，我们是本地，用不上 |
| **STS 临时令牌** | 腾讯云 / 火山 / 阿里云 | ✅ **推荐** | 有时效、可设短、泄露损失小。比长期 AK 安全 |
| 长期 AK/SK | 腾讯云 / 火山 | 需你去控制台 | 最通用，但要保管好 |

### 如果你更倾向 STS 临时令牌

- **腾讯云**：CAM 控制台 `sts:AssumeRole` → 拿 `TmpSecretId/TmpSecretKey/Token` 三元组。
  我这边多传一个 `token` 参数即可（`credential.Credential(id, key, token)`），代码只需多一行。
- **火山引擎**：IAM → 角色 → 扮演 → 拿 `AccessKeyId/SecretAccessKey/SessionToken`。
  SDK 已认 `VOLCENGINE_SESSION_TOKEN` 环境变量，**零改代码**。

**怎么选**：图省事给长期 AK（我按 §6 红线存 600，不进 git/聊天）；
图安全给 STS 临时令牌（我会加个过期重试，到期你续一次）。两者我都能接，你告诉我哪种。
