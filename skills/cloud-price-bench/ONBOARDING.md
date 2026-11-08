# 8 云接入清单 —— 谁要 AK、放哪、怎么验

> 实测日期 2026-10-31。原则：**能匿名就不配凭据**（零费用、只读、无泄露面）。
> 已匿名跑通的 4 朵云，你什么都不用做。

## 一、已就绪（6 朵）

| 云 | 凭据 | 数据源 | 验一把 |
|---|---|---|---|
| AWS | **无** | `b0.p.awsstatic.com` 静态价表（1348 行） | `python3 bench.py compare --shape 4c16g` |
| Azure | **无** | 官方 Retail Prices API | 同上 |
| 阿里云 | **AK（本机已有）** | ECS `DescribePrice` | 同上 |
| OCI | **无** | `apexapps.oracle.com/cetools` 价目 API（668 SKU） | 同上 |

阿里云 AK 已存在于 `~/.aliyun/config.json`（profile `default`，region `cn-hangzhou`），
权限 600，skill 运行时只读、不复制、不落盘。**无需你操作。**

注意：**AWS 官方 Price List API 与 awslabs MCP 必须 AK/SK**（已三重实测，
`Unable to locate credentials` / 假 AK 返回 `UnrecognizedClientException`）。
本环境改用官方发布的静态价表端点，所以 AWS 免 AK —— 这是绕过，不是 AWS 官方匿名 API。

## 二、待补 2 朵：要什么、放哪

| 云 | 要什么 | 放哪（权限 600） | 状态 |
|---|---|---|---|
| GCP | **API Key**（不是 AK/SK） | `~/.config/gcp-billing.key` | 匿名路径全 403/404，确认封死 |
| 腾讯云 | SecretId + SecretKey | `~/.tencentcloud/credentials` | 需 TC3 签名；定价页还有登录态+反爬 |
| 华为云 | AK + SK（IAM 用户） | `~/.huaweicloud/credentials` | 当前只有 `application_id`，无 AK/SK |
| 火山引擎 | AK + SK | `~/.volcengine/credentials` | `open.volcengineapi.com` 需签名 |

### ~~GCP：只要一个 API Key~~ —— 已匿名攻破，见第四节

1. 打开 Cloud Console → APIs & Services → **启用 Cloud Billing API**
2. Credentials → Create Credentials → **API Key**
3. 建议限制该 Key 只允许 Cloud Billing API
4. 存到本机：
   ```bash
   echo -n '你的KEY' > ~/.config/gcp-billing.key && chmod 600 ~/.config/gcp-billing.key
   ```
5. 验收：
   ```bash
   curl -s "https://cloudbilling.googleapis.com/v1/services?key=$(cat ~/.config/gcp-billing.key)" | head -c 200
   ```
   返回含 `services` 即通。**不需要服务账号 JSON，也不需要 OAuth。**

### 腾讯云 / 火山引擎：需要 AK+SK（华为云已匿名攻破）

都是成对密钥，控制台 → 访问密钥 → 新建，建议**只给只读账单/询价权限**的子账号。

放置（文件权限必须 600）：
```bash
mkdir -p ~/.tencentcloud ~/.huaweicloud ~/.volcengine
cat > ~/.tencentcloud/credentials <<'EOF'
SecretId = 你的Id
SecretKey = 你的Key
EOF
chmod 600 ~/.tencentcloud/credentials
```

腾讯云额外提示：`DescribeZoneInstanceConfigInfos` / `InquiryPriceRunInstances`
是它定价页真实在用的接口，签名走 TC3-HMAC-SHA256。

## 三、给我凭据之后我会做什么（你不用管细节）

1. 写 `adapters/<云>.py`，实现 `query()` 返回 USD/hr
2. `clouds.yaml` 里 `status: NEED_CRED` → `READY`
3. 跑 `bench.py compare --shape all` 校准各档候选 SKU（按 vCPU/内存核对，不猜）
4. 更新 `SKILL.md` 的实测结论表
5. 重跑 `gen_dashboard.py`，把新云补进全景图的比价区

**报告层不用改** —— 这是当初设计好的插口。

## 四、红线

- 凭据文件一律 600，**绝不进 git、绝不贴聊天、绝不写进 skill 文件**
- 只读用途：询价/账单只读即可，**不要给停机、删除、创建资源的权限**
- Azure 保持只读，不自动停资源

---

## 匿名端点探测记录 2026-10-31

范围：gcp / tencent / huawei / volcengine 四朵云，目标找到**无需 AK/SK、无需登录**即可
curl 到的官方价格端点。所有候选均实测（curl + `User-Agent: Mozilla/5.0`），记录 HTTP 码与返回片段。
红线遵守：零费用、未注册任何账号、未使用信用卡、未写入任何凭据。

### 结论速览

| 云 | 可用匿名端点 | 凭据 | 结论 |
|---|---|---|---|
| huawei | `portal-intl.huaweicloud.com/.../productInfo?urlPath=ecs` | **无** | ✅ **可用**，已写适配器 |
| gcp | 无 | 需 API Key | ❌ 无解（官方 API 明确拒绝未注册调用方） |
| tencent | 无 | 需登录 CSRF / TC3 签名 | ❌ 无解（CGI 恒返回 code:9） |
| volcengine | 无 | 需 AK 签名 | ❌ 无解（网关恒返回 UnauthorizedAccess） |

### 1. 华为云 —— ✅ 匿名可用（本次唯一成果）

入口发现路径：`https://www.huaweicloud.com/pricing/calculator.html` → 页面引入
`https://portal.hc-cdn.com/CBC-PortalCalculator/11.4.201/framework.js`（2.8 MB）→ 从 JS 中
提取出价目接口。

**端点（匿名，无任何 header 要求）：**

```
https://portal-intl.huaweicloud.com/api/calculator/rest/cbc/portalcalculatornodeservice/v4/api/productInfo?urlPath=ecs
https://portal.huaweicloud.com/api/calculator/rest/cbc/portalcalculatornodeservice/v4/api/productInfo?urlPath=ecs
```

| 站点 | 凭据 | HTTP | 响应体积 | region | 币种 |
|---|---|---|---|---|---|
| intl | 无 | **200** | 5,068,719 B | `ap-southeast-1` | **USD** |
| cn | 无 | **200** | 7,551,671 B | `cn-north-4` | **CNY** |

返回结构：`{"product": {"ec2_vm": [...], "ec2_vm.image": [...], ...}, "region": ..., "period": {...}}`
其中 `ec2_vm` 中国站 3191 条 / 国际站 2203 条。单条样例（截取）：

```json
{"resourceSpecCode":"s6.large.2.linux","cpu":"2dataInfo_36_","mem":"4BSSUNIT.pluralUnit.102",
 "instanceArch":"x86","performType":"General Computing","series":"S6","image":"Linux",
 "planList":[{"billingMode":"MONTHLY","amount":28.8},
             {"billingMode":"ONDEMAND","billingEvent":"event.type.vmduration",
              "measureUnit":4,"usageFactor":"Duration","amount":0.066}]}
```

**能否拿到 Linux 通用型 x86 按量单价：能。** 筛选条件 `resourceSpecCode` 以 `.linux` 结尾 +
`instanceArch == "x86"` + `planList` 中 `billingMode == "ONDEMAND"` 且
`billingEvent == "event.type.vmduration"` → `amount` 即**小时单价**。
国际站筛出 418 条符合；中国站 747 条。

实测（国际站 ap-southeast-1，USD/hr，Linux x86，已排除 T 系列突发型）：

| 规格 | 最低价 SKU | USD/hr |
|---|---|---|
| 2c4g | `s3.large.2.linux` / `s2.large.2.linux` | 0.060 |
| 2c8g | `s6.large.4.linux` | 0.080 |
| 4c16g | `s6.xlarge.4.linux` | 0.160 |
| 8c32g | `s6.2xlarge.4.linux` | 0.320 |

实测（中国站 cn-north-4，CNY/hr）：2c4g `x1.2u.4g.linux`=0.225；8c32g `x1.8u.32g.linux`=1.35。

**已知限制：** 接口不支持按 region 过滤（实测 `regionId=` 等参数无效），恒返回站点默认区域
价格快照；华为云各区域同规格价差极小，比价可接受，但需在报告里注明。

其他华为端点（均匿名可达但无价值）：`inquiry/resource` → 400 校验循环；`v1/exchange-rate`
→ 400 缺 `page_no`；`export/productlist` → 400 `invalid urlPath`；
`res-static.hc-cdn.cn/pricecalculator/*` → **403**。

### 2. GCP —— ✅ 已攻破（2026-10-31 晚，匿名第三方聚合站）

官方通道确实全废（下表保留，说明为什么不能走官方），但找到了**匿名可用旁路**：

| 端点 | 凭据 | HTTP | 结果 |
|---|---|---|---|
| `cloudbilling.googleapis.com/v1/services` | 需 key | **403** | `Method doesn't allow unregistered callers`（官方 API 必须 API Key） |
| `www.gstatic.com/cloudpricingcalculator/static/data/pricelist.json` | 无 | **404** | 历史静态价目表已下线 |
| `cloudpricingcalculator.appspot.com/static/data/*.json` | 无 | **404** | 同上 |
| `cloud.google.com/products/compute/pricing` | 无 | 200（2.0 MB） | 纯 JS 渲染，`e2-standard` 出现 **0** 次，抓不到价 |
| ✅ **`gcloud-compute.com/<机型>.html`** | **无** | **200** | **可用**：一页覆盖 **42 个区域**，on-demand USD/hr 直读 |
| ✅ `cloudprice.net/gcp/compute?region=asia-southeast1` | 无 | 200 | 备用源：SSR 内嵌数组，一次拿 500+ 机型（需解析 HTML） |

**解析方式**：机型页的 `<td title="...">` 里带完整描述，正则即可取：
`Costs per hour for machine type (?P<mtype>\S+) in region (?P<region>[a-z0-9-]+): (?P<price>[\d.]+) USD`
同一 region 第一条是 on-demand，其后依次是 spot / month / 1Y CUD / 3Y CUD，用 `setdefault` 保住首条。
机型规格（vCPU/内存）在 `<meta name="description">` 里：
`... with 2 vCPU and 4 GB memory. Available in 42 ...`

**实测（us-central1，2026-10-31）**：

| 机型 | vCPU/内存 | USD/hr |
|---|---|---|
| e2-medium | 2 / 4GB | 0.0335 |
| e2-standard-2 | 2 / 8GB | 0.0670 |
| e2-standard-4 | 4 / 16GB | 0.1340 |
| e2-standard-8 | 8 / 32GB | 0.2680 |

**⚠️ 必须披露**：`gcloud-compute.com` 是**第三方聚合站，非 Google 官方**。
官方匿名通道已确认全部不可用，这是唯一零凭据路径。对客户的正式报价若需官方口径，
则仍需补一个免费 API Key（见第二节，key 文件 600 权限）；内部比价/选型用第三方源足够。

**坑**：`gcloud-compute.com/instances.html` 列表页上的 0.0809 是**全区域含 SUD 均价**，
不是 us-central1 单价 —— 按区域必须走机型详情页。

### 3. 腾讯云 —— ❌ 需登录态 CSRF，无匿名路径

| 端点 | 凭据 | HTTP | 返回前 300 字符 |
|---|---|---|---|
| `buy.cloud.tencent.com/cgi/v2/pricecenter/getProductPageConfig?goodsName=cvm` | 需登录 | **200** | `{"code":9,"msg":"验证CSRF失败，请重新登录","uiMsg":"登录态验证失败，请重新登录 [流水号: 1gz_...]","extraMsg":"","returnCode":0}` |
| `buy.cloud.tencent.com/cgi/api?i=region/index&cmd=cvm` | 需登录 | **200** | 同上 code:9 |
| `buy.cloud.tencent.com/cgi/area/queryCvmRegion` | 需登录 | **200** | 同上 code:9 |
| `buy.tencentcloud.com/cgi/v2/pricecenter/getProductPageConfig`（国际站） | 需登录 | **200** | 同上 code:9 |
| `buy.tencentcloud.com/cgi/v2/pricecenter/getCalculatorJsConfig` | 需登录 | **200** | 同上 code:9 |
| `cloud.tencent.com/...` 同路径 | — | **404** | 不存在 |
| `buy.cloud.tencent.com/pricecenter/overview/cvm` | — | **500** | — |
| `cloud.tencent.com/api/cvm/price` | — | **404** | HTML 404 页 |
| `cvm.tencentcloudapi.com/`、`api.tencentcloudapi.com/` | **需 TC3 签名** | **200** | `{"Response":{"Error":{"Code":"MissingParameter","Message":"The request is missing the required parameter 'Timestamp'."}}}`（签名前先缺参，补参后仍需 `X-TC-*` 签名头） |

补充探测（均无效）：
- 带匿名 cookie（`language=zh`）+ `Referer` + `X-Requested-With` 重打 CGI → **仍 code:9**（CSRF 与登录态绑定，cookie 无法绕过）
- 页面内嵌 `window.__PREFETCH_DATA__`（`buy.cloud.tencent.com/price/cvm/calculator`，200/172,186 B）
  解析结果：只有页面配置（`needLogin: 0`、JS 资源路径、`owner` 名单），**无任何价格表**
- `cvm_pricing.f1baf0a21219d327f728.js`（1,021,425 B）全文仅含 `/cgi/api?i=region/`、
  `/cgi/area/queryCvmRegion` 两条 CGI，无内嵌价格数据
- `product.8731a944f4228d770357.js`（3,099,055 B，价格计算器主包）→ 无任何价格表、无 `.json` 价目引用
- `cloud.tencent.com/product/cvm/pricing`、`/document/product/213/2176`、`/11518`、轻量
  `lighthouse/pricing` → 200 但均为文案页，无结构化价格（lighthouse 页仅包年包月整包价 459/510/1020 元）

**能否拿到 Linux 通用型 x86 按量单价：否。** 唯一的按量（元/小时）数据源是需登录 CSRF 的
pricecenter CGI 或需 TC3 签名的 `InquiryPriceRunInstances` / `DescribeZoneInstanceConfigInfos`。

### 4. 火山引擎 —— ❌ 需 AK 签名，无匿名路径

| 端点 | 凭据 | HTTP | 返回前 300 字符 |
|---|---|---|---|
| `www.volcengine.com/api/price/ecs` | 需授权 | **200** | `{"ResponseMetadata":{"RequestId":"...","Service":"Platform","Error":{"Message":"未授权访问","Code":"UnauthorizedAccess"}}}` |
| `www.volcengine.com/api/price/ecs/price` | 需授权 | **200** | 同上 `UnauthorizedAccess` |
| `www.volcengine.com/api/billing/price/query` | 需授权 | **200** | 同上 |
| `www.volcengine.com/api/calculator/price` | 需授权 | **200** | 同上 |
| `www.volcengine.com/api/product/price` | 需授权 | **200** | 同上 |
| `www.volcengine.com/api/ecs/price/list`、`/api/commodity/price` | 需授权 | **200** | 同上 |
| `console.volcengine.com/api/price` | 需登录 | **403** | `{"ResponseMetadata":{...,"Error":{"Code":"Forbidden","Message":"Method forbidden"}}}` |
| `console.volcengine.com/ecs/price` | — | **200**（118,001 B） | HTML 控制台壳，无价格（需登录后才渲染） |
| `open.volcengineapi.com/` | **需签名** | **400** | `{"ResponseMetadata":{...,"Error":{"CodeN":100002,"Code":"MissingParameter","Message":"The request is missing Action..."}}}` |
| `portal.volcengine.com/api/price` | — | **000** | 连接失败（域名不可达） |
| `calc.volcengine.com/` | — | **000** | 连接失败 |

补充探测：
- `www.volcengine.com/product/ecs/pricing`（200/169,633 B）与 `/calc`（200/330,342 B）：
  仅 `window.gfdatav1`（模块路由表）与 `window.__ENV`，**无内嵌价格表**。
  页内出现的 `0.128`/`0.218`/`0.679` 等数字经上下文核对是 **JS bundle 版本号**（`1.0.0.128`），非价格。
- `www.volcengine.com/docs/6396/75422`（ECS 定价文档，200/1,097,214 B）：全文无 `ecs.xxx` 机型、
  无 `元/小时` 价格（文档价格表由前端异步加载）
- `portal.volccdn.com/.../main.383cfaf3.js`（37 KB）：只有产品路由，无价格 API

**能否拿到 Linux 通用型 x86 按量单价：否。** 所有 www 域 `/api/*` 经统一网关，未签名一律
`UnauthorizedAccess`；开放 API `open.volcengineapi.com` 强制签名。

### 适配器产出

已产出 **3 个适配器**（华为云 + GCP 匿名攻破，阿里云原有）：

### `adapters/huawei.py`（2026-10-31 攻破，匿名）

- 站点：`intl`（默认，USD，region ap-southeast-1）/ `cn`（CNY，region cn-north-4）
- `query(vcpu, mem, site, allow_burst)` → 该规格下最低价 SKU，返回 `usd_hr`；
  cn 站点按 `CNY_USD_RATE`（默认 0.14，与 bench.py 阿里云口径一致）换算
- `list_shapes(vcpu, mem, site, limit)` → 候选清单（含 burst 标记，便于核对）
- 默认排除 T 系列突发性能实例（`allow_burst=False`），对齐 bench.py「通用型非突发」口径
- 缓存：5~7 MB 价目表落到 `adapters/.cache/huawei_ecs_{site}.json`，TTL 7 天
- 实测四档：2c4g 0.060 / 2c8g 0.080 / 4c16g 0.160 / 8c32g 0.320 USD/hr

### `adapters/gcp.py`（2026-10-31 攻破，匿名第三方源）

- 数据源 `gcloud-compute.com/<机型>.html`，正则解析 on-demand USD/hr，默认区域 `us-central1`
- `query(mtype, region)` → `{'shape','vcpu','mem_gb','usd_hr','region','currency','unit','exact','raw'}`
- `list_shapes(region, limit)` → 已知机型清单（e2-medium / e2-standard-2/4/8/16 / n2-standard-2/4/8）
- `prices(mtype)` → `{region: usd_hr}` 全 42 区域
- 缓存：HTML 落 `adapters/.cache/gcp_<机型>.html`，TTL 7 天
- 实测四档：2c4g 0.0335 / 2c8g 0.0670 / 4c16g 0.1340 / 8c32g 0.2680 USD/hr

### 未产出适配器

tencent / volcengine 两朵云**确认无匿名旁路**，需按上文第二节补 AK/SK。

**当前战果：8 云已自配 6 云，其中 5 云零凭据匿名**（AWS / Azure / OCI / 华为云 / GCP），
阿里云走已有 `~/.aliyun` AK。
