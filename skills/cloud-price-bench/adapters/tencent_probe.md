# 腾讯云 CVM 匿名价格探针报告

探测日期：2026-10-31 ｜ 约束：零凭据、零花费、只读 GET ｜ 目标：Linux/x86 通用型按量小时价（CNY/hr 或 USD/hr）

## 结论（置顶）

**不存在完全匿名、零凭据的腾讯云 CVM「按量付费小时价」数据源。**

- 所有能给出单价的官方接口都要求登录态（CSRF）或 API 密钥（TC3-HMAC-SHA256）。
- **新发现**：`cloud.tencent.com/product/cvm` 与 `/product/lighthouse/pricing` 页面 HTML 内嵌 `pricings.price` 数值，可匿名 curl 200 解析 —— 但**全部是包年包月（元/年、元/月）活动价，且含系统盘 + 带宽**，不是按量小时价，也不是纯实例刊例价。
- 因此本轮**无法产出可直接与 AWS/GCP/OCI On-Demand 混排的 CVM 单价**。建议 `bench.py` 把腾讯云 CVM 标为「无匿名按量价，需人工补」。

---

## 一、实测可用（200 + 可解析数值），但口径不符

### 1.1 CVM 产品页内嵌活动价（元/年）

```bash
curl -s --compressed -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120" -L \
  "https://cloud.tencent.com/product/cvm/pricing" -o /tmp/cvmp.html
# 200, ~29KB（压缩）/ ~168KB（解压）
```

返回片段（HTML 内嵌 `__NEXT_DATA__` 式 JSON）：

```
{"title":"标准型SA5 2核","region":"北京","specs":[
  {"label":"内存","value":"4G"},{"label":"系统盘","value":"50G"},
  {"label":"带宽","value":"1Mbps"}],
 "pricings":{"price":"1567","unit":"元/年"},
 "button":{"to":"https://buy.cloud.tencent.com/cvm?...instanceType=SA5.MEDIUM4&...&timeSpan=12"}}
```

解析出的机型 ↔ 价（**均为 元/年，含 50G 系统盘 + 1Mbps 带宽，timeSpan=12**）：

| instanceType | 页面标题 | 内存 | 价格 | 单位 |
|---|---|---|---|---|
| SA5.MEDIUM4 | 标准型SA5 2核 | 4G | 1567 | 元/年 |
| BF1.MEDIUM2 | 蜂驰型BF1 2核 | 2G | 531 | 元/年 |
| S6.2XLARGE16 | 标准型S6 8核 | 16G | 5719 | 元/年 |
| S6.4XLARGE64 | 标准型S6 16核 | 64G | 16410 | 元/年 |
| C6.LARGE8 | 计算型C6 4核 | 8G | 4756 | 元/年 |
| C6.4XLARGE64 | 计算型C6 16核 | 64G | 26668 | 元/年 |
| C5.LARGE8 | 计算型C5 4核 | — | 4358 | 元/年 |
| M6.MEDIUM16 | 内存型M6 2核 | 16G | 3348 | 元/年 |
| D3.2XLARGE32 | 大数据型D3 8核 | 32G | 14573 | 元/年 |
| GT4/GN8/GI3X/GN7vw | GPU 型 | — | 13614~167286 | 元/年 |

**四档覆盖：极差。**

| 档位 | 机型 | 是否命中 | 说明 |
|---|---|---|---|
| 2C4G | `SA5.MEDIUM4` | ✅ | 1567 元/年（SA5 为 AMD 经济型，非 S5 通用型） |
| 2C8G | `S5.MEDIUM8` | ❌ | 页面无此规格 |
| 4C16G | `S5.LARGE16` | ❌ | 页面仅 `S6.2XLARGE16`=8C16G、`C6.LARGE8`=4C8G |
| 8C32G | `S5.2XLARGE32` | ❌ | 仅 `D3.2XLARGE32`（大数据型，带本地盘） |

换算示例（**仅演示，不可与 On-Demand 混排**）：
`1567 元/年 ÷ 12 ÷ 730 = 0.1789 元/时 ≈ $0.0246/hr`（按 7.27 汇率）

### 1.2 轻量应用服务器 Lighthouse 价页（元/月）

```bash
curl -s --compressed -A "Mozilla/5.0 Chrome/120" -L \
  "https://cloud.tencent.com/product/lighthouse/pricing" -o /tmp/lh.html
# 200, ~27KB
```

返回片段：

```
{"title":"通用型套餐（进阶）","region":"上海/北京/广州/成都/南京",
 "specs":[{"label":"CPU&内存","value":"2核 4GB"},{"label":"SSD 系统盘","value":"100GB"},
          {"label":"带宽","value":"7Mbps"},{"label":"流量包","value":"1000GB/月"}],
 "pricings":{"price":"100","unit":"元/月","approximation":""}}
```

| 套餐 | 规格 | 中国内地 | 境外（新/东/硅/法/首/雅） |
|---|---|---|---|
| 入门型 | 2C2G / 40G / 3M | 45 元/月（459 元/年 85折） | 30 元/月（360 元/年） |
| 入门型（基础） | 2C2G / 50G / 4M | 50 元/月 | 33 元/月（396 元/年） |
| **通用型（进阶）** | **2C4G / 100G / 7M** | **100 元/月** | **72 元/月（864 元/年）** |
| 通用型（专业） | 4C8G / 180G / 12M | 245 元/月 | 260 元/月 |
| 锐驰型 | 2C2G / 40G / 200M 无限流量 | 45 元/月 | 40 元/月 |
| 锐驰型 | 4C8G / 120G / 200M | 230 元/月 | 235 元/月 |

**四档覆盖：仅 2C4G；2C8G / 4C16G / 8C32G 均无。**
换算：`100 元/月 ÷ 730 = 0.1370 元/时 ≈ $0.0188/hr`。
**口径污染更严重**：Lighthouse 价含 SSD 系统盘 + 峰值带宽 + 月流量包，与 CVM 纯实例完全不可比；且 Lighthouse 是共享/突发型，不属于通用型 S5 家族。

### 1.3 机型规格表（无价，仅规格映射，参考价值最高）

```bash
curl -s --compressed -A "Mozilla/5.0 Chrome/120" -L \
  "https://cloud.tencent.com/document/product/213/11518" -o /tmp/inst.html
# 200, 598545
```

片段：`S5.MEDIUM4 2 4 / S5.MEDIUM8 2 8 / S5.LARGE16 4 16 / S5.2XLARGE32 8 32`
→ 四档映射：**2C4G=`S5.MEDIUM4`、2C8G=`S5.MEDIUM8`、4C16G=`S5.LARGE16`、8C32G=`S5.2XLARGE32`**。
全文 `元/小时` 计数 0、`USD` 计数 0 → **无任何单价**，只能做规格↔机型映射。

### 1.4 计费规则（无刊例价）

```bash
curl -s --compressed -A "Mozilla/5.0 Chrome/120" -H "Accept-Language: zh-CN" -L \
  "https://cloud.tencent.com/document/product/213/2176"
# 200, 64800
```

只有折扣规则，无绝对价格：包年包月时长折扣（A/B/C 类 87/78/73/64/54/39/33/27 折…）、按量三阶阶梯（T2=T1×50%、T3=T1×34%）、境外按量 78 折。

---

## 二、实测不可用（附原因）

| 端点 | 结果 |
|---|---|
| `buy.tencentcloud.com/cgi/v3?i=cvm/DescribeZoneInstanceConfigInfos`、`InquiryPriceRunInstances`、`/cgi/api?i=...`（含带 `uin=0`、`region=ap-singapore`） | 200 但 `{"code":9,"msg":"验证CSRF失败，请重新登录"}`；国际站同样 |
| `buy.cloud.tencent.com/cgi/v2/pricecenter/getProductPageConfig?productCode=cvm`、`getCalculatorJsConfig`、`getPriceTabData`、`?needLogin=0` | 同上 code 9 |
| **新增** `buy.cloud.tencent.com/cgi/v2/trade/queryPrice?productCode=cvm&subProductCode=cvm&timeSpan=1&timeUnit=h`（及 `p_cvm`、带 regionId/zoneId/instanceType/payMode） | 200 但 `{"code":4,"msg":"参数不正确"}`；schema 在 `price/product.8731a944...js` 中要求 `productCode,subProductCode,timeSpan,timeUnit` + 登录态 |
| **新增** `buy.cloud.tencent.com/cgi/v2/config/getPriceTabData`、`/cgi/v2/buy/index` | code 9 / code 4 |
| `cvm.tencentcloudapi.com/?Action=DescribeZoneInstanceConfigInfos&...` | 200 但 `{"Response":{"Error":{"Code":"MissingParameter","Message":"...required parameter SecretId"}}}` → 需 TC3 签名 |
| `www.tencentcloud.com` CGI / `/pricing/cvm`（curl） | 返回 ~989 字节 EO 反爬挑战（`EO_Bot_Ssid`/`__tst_status`）；改用 Python urllib 可拿 172KB/361KB 完整页，但 `USD` 0、`$x.xx` 0、价表 0（出现的 `10.8035` 等小数是 SVG path 坐标，非价格） |
| `buy.tencentcloud.com/pricing/cvm` 完整 HTML | 168KB，但 `"price":` 计数 0、`元/小时` 0、`unitPrice` 0；价由 JS 从上述 CGI 拉 |
| `cvm_pricing.*.js`（356KB）+ `price/product.*.js`（755KB） | 内 `unitPrice` 仅为 UI 字段名，**无硬编码价表** |
| `calc.cloud.tencent.com/` | curl 000（DNS/连接失败）；`cloud.tencent.com/calc` 404 |
| `cloudcache.tencent-cloud.com`、`main.qcloudimg.com` 静态价文件 | 未发现任何价格 JSON/CSV |
| cloudprice.net：`/tencent`、`/tencent-cloud-pricing`、`/api/providers` | 全部 404（仅覆盖 AWS/GCP/Azure） |
| sparecores keeper API `?vendor=tencent` | **422** `"Input should be 'alicloud','aws','azure','gcp','hcloud','ovh','upcloud' or 'vultr'"` → 明确无腾讯云 |
| ec2instances.info / vantage-sh | 200 659KB，但 grep `tencent/qcloud` = 0（仅 AWS） |
| cloud-instance-pricing.com、instances.vantage.sh、cloudcost.today、cloudorado.com | 000 / 500，已挂或不覆盖 |
| GitHub raw 含腾讯云价 JSON 仓库 | 未找到（GitHub code/search API 需鉴权 401/403） |

---

## 三、口径警告（必读）

1. **包年包月 ≠ On-Demand。** 1.1 / 1.2 拿到的全是 `元/年`、`元/月`，换算公式：
   - `元/年 ÷ 12 ÷ 730 = 元/小时`
   - `元/月 ÷ 730 = 元/小时`
   - `元/小时 ÷ 汇率 ≈ USD/hr`
2. **换算结果仍不可与 AWS/GCP/OCI On-Demand 混排**，原因：
   - 腾讯云按量有**三阶阶梯**：T1 全价、T2 = T1×50%、T3 = T1×34%（境外另叠 78 折），按量实付随用量漂移；
   - 包年包月有**时长折扣**（最长 27 折），页面价已是折后或活动价，非刊例价；
   - 页面价**含云盘 + 公网带宽 + 流量包**，AWS/GCP/OCI 的 On-Demand 通常是裸实例价，需剔除存储与网络才能比；
   - 中国内地地域价含税与服务差异，与境外 USD 价不是同一市场。
3. 正确做法：跨云比价时腾讯云 CVM 一列标注 `N/A（无匿名按量价）`，或单独开一列「包年包月折算参考（不可比）」。

## 四、后续建议

- **（a）唯一拿真价途径**：人工登录定价中心 / 价格计算器导出，或控制台选型页手抄四档按量小时价，作为静态基准表补进 `bench.py`。
- **（b）自动化替代**：申请只读子账号密钥走 `InquiryPriceRunInstances`（TC3 签名）——**违反零凭据约束，本报告不推荐**。
- **（c）代码层面**：`cloud-price-bench` 目前有 `huawei.py`（匿名 portal 计算器）、`gcp.py`（gcloud-compute.com）、`oci.py`（apexapps）、`alicloud.py`（需 AK）。腾讯云**无法仿照 huawei/gcp 写匿名 adapter**，建议新增 `tencent.py` 时默认返回 `status=NO_ANONYMOUS_PRICE` 并读取人工维护的 fallback 表。
- 备注：`curl` 对 `*.tencentcloud.com` 常触发 EO 反爬，改用 `python3 urllib`（普通 UA）可拿完整 HTML；抓 `cloud.tencent.com` 文档须加 `--compressed`。全程未绕过任何登录或签名机制。
