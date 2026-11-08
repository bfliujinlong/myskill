# 火山引擎 ECS 匿名价格探针报告

探测日期：2026-10-31（本轮为第 2 轮复核，前序 5 个方向已全为负）
约束：零凭据、零花费、不注册账号、不刷信用卡、只读 GET（不 POST 建资源）、报告内无任何 key/密码。
目标：Linux / x86 / 通用型 **按量计费** 单价（CNY/小时），需能对应 2C4G / 2C8G / 4C16G / 8C32G 四档。

---

## 结论（置顶）

**结论：必须 AK/SK。**

火山引擎 ECS 的机型单价在全网范围内**不存在任何完全匿名、零凭据、可 curl 200 解析的按量计价数据源**。
所有能给出单价的路径（控制台 / 价格计算器 / OpenAPI `open.volcengineapi.com`）都要求登录态或 AK/SK 签名；
第三方聚合站（cloudprice.net、sparecores、vantage、infracost）**均未收录火山引擎**。
建议 `bench.py` 将火山引擎 ECS 标为「无匿名按量价，需人工补 / 需 AK/SK」。

---

## 结论速览

| 方向 | 端点代表 | 匿名可用 | 能否解析机型单价 |
|---|---|---|---|
| 官网价格页 /product/ecs/pricing | www.volcengine.com | ❌（200 但 SPA 空壳） | ❌ |
| 价格计算器 /price/calculator | www.volcengine.com | ❌（200 但纯 JS 渲染） | ❌ |
| www/console 价格 API | /api/price/inquiry、/api/billing/price | ❌（200 body=未授权访问） | ❌ |
| console 网关 | console.volcengine.com/api/* | ❌ 403 | ❌ |
| OpenAPI | open.volcengineapi.com | ❌ 400（缺签名） | ❌ |
| 文档站 docs | /docs/ecs/pay-as-you-go 等 | ❌（200 但仅示意举例） | ❌ |
| CDN 静态资源 | portal.volccdn.com / bytetos / gcloudcache | ❌（仅站点配置 & CSS 类名） | ❌ |
| 国际站 BytePlus | www.byteplus.com/en/... | ❌（数字均为营销套餐/版本号） | ❌ |
| 第三方聚合 | cloudprice.net / sparecores / vantage / infracost | ❌（未收录 volcengine） | ❌ |
| GitHub 价格仓库 | volcengine-pricing-quote-skills 等 | ❌（需 Playwright 登录下载 CSV） | ❌ |
| Wayback 历史快照 | archive.org | ❌ 无快照 | ❌ |
| 移动站 | m.volcengine.com | ❌ HTTP 000（无此主机） | ❌ |

---

## 一、可用端点

**无。** 没有任何端点满足「200 + 可解析出具体机型单价」。

---

## 二、不可用端点及原因

### A. 官网价格页 / 计算器（200，但纯前端渲染，无内嵌价格）

```bash
curl -sL --compressed -A "Mozilla/5.0" "https://www.volcengine.com/product/ecs/pricing" -o /tmp/volc_pricing.html -w "%{http_code} %{size_download}\n"
# 200 169633
grep -c "元" /tmp/volc_pricing.html        # 0
grep -c "ecs\." /tmp/volc_pricing.html     # 0
grep -c "<table" /tmp/volc_pricing.html    # 0
```

判定：HTML 只有 `arco-spin` 骨架占位，价格数据由鉴权 XHR 拉取，静态 HTML 中不含任何单价。
同类为负：`/product/ecs/price`、`/pricing?product=ECS&tab=2`（200/50457 B）、`/price/calculator`（200/330385 B）、
`/activity/ecs-intel`、`/activity/ecs-amd`、`/activity/ecs-amd-2024`（200/67651 B 空壳）、
`/en/product/ecs/pricing`、`/en/price/calculator`（200，**无 USD 单价**）。

### B. www 价格 API（HTTP 200，但 body 恒为未授权）

```bash
for p in /api/price/inquiry /api/billing/price /api/ecs/price /api/price/query /api/ssr/prefetch_common; do
  curl -sL -A "Mozilla/5.0" "https://www.volcengine.com$p" -w " [$p %{http_code}]\n"
done
```

统一返回（158 B，HTTP 200，极易误判为可用）：

```
{"ResponseMetadata":{"RequestId":"...","Service":"Platform","Error":{"Message":"未授权访问","Code":"UnauthorizedAccess"}}}
```

其他：
- `www.volcengine.com/api/price` → 404；`/api/v2/top/price` → 404
- `/api/passport/account/getUser` → 401
- `/api/bee/getJson` → 200 但 body 仅 `{}`；`/api/bee/publish/getJson?name=ecs_pricing` → UnauthorizedAccess
- `/api/doc/getDocDetail?docId=68526` → `{"Code":"ParameterMissing","Message":"The parameter [LibraryCode or DocumentCode] is missing."}`（补齐参数仍走鉴权）

### C. console 网关（403 / 登录页）

```bash
curl -sL -A "Mozilla/5.0" "https://console.volcengine.com/api/billing/price" -w " [%{http_code}]\n"        # 403
curl -sL -A "Mozilla/5.0" "https://console.volcengine.com/api/ecs/DescribeInstanceTypes" -w " [%{http_code}]\n" # 403
curl -sL -A "Mozilla/5.0" "https://console.volcengine.com/price/api/ecs" -w " [%{http_code}]\n"            # 200 但返回登录页 HTML
curl -sL -A "Mozilla/5.0" "https://console.volcengine.com/ecs/region:ecs+cn-beijing/instance/create" -w " [%{http_code}]\n" # 200 登录/SPA 壳
```

### D. OpenAPI（已知失败，本轮不重复验证，仅登记）

- `open.volcengineapi.com`、`ecs.cn-beijing.volcengineapi.com` → 400（缺签名，强制 AK/SK）
- `api.volcengine.com` → 302 跳转到 `/api-explorer` 网页
- `calc|price|pricing|buy|order.volcengine.com` → HTTP 000（无此主机 / DNS 不存在）

### E. 文档站（200 且正文随 HTML 下发，但只有示意举例，无机型价目表）

```bash
curl -sL --compressed "https://www.volcengine.com/docs/ecs/pay-as-you-go?lang=zh" -o /tmp/doc_payg.html -w "%{http_code} %{size_download}\n"
# 200 1157603
```

正文确含单价字样，但为**计费规则示意举例**，非价目表：

> 「某一规格的实例单价为0.8元/小时」……「请在价格计算器查看实例价格……以控制台下单为准」

其他文档（`/docs/ecs/instance-type-billing` 200/1286397 B 只有包年包月/按量/抢占/预留对比表；
`/docs/6396/68526`、`67724`、`68419`、`1864867`、`/docs/ecs/instance-types|instance-specifications|billing|billable-items`）→ 均 200，
但正文未随 HTML 下发，`vCPU` 命中 0、`元` 命中 12 全部来自导航菜单、`g3i` 仅出现在菜单标题。
文档 API：`/api/doc/getDocContent` 404、`/api/doccenter/docDetail` → UnauthorizedAccess。
页面上无任何 `.csv/.xlsx/.zip` 价目表下载链接（PDF 仅叙事文档）。

### F. BytePlus 国际站（200，但数字全是营销套餐/版本号/CSS，非 ECS 小时价）

- `www.byteplus.com/en/product/ecs/pricing`、`/en/pricing?product=ECS`、`/product/ecs/pricing` → 200（arco-spin 占位）
- 页面抓到的 `$4.50 / $6.99 / 0.15 / 0.45 / 0.636 / 14.059` 等 → 分别为套餐价、SDK 版本号、CSS 动画延迟、SVG path 数据
- `docs.byteplus.com/en/docs/ecs/instance-types|instance-type-billing|pay-as-you-go` → 200（~991 KB），`ecs.*` 机型价匹配 0

### G. 第三方聚合站（未收录火山引擎）

```bash
curl -sL -o /dev/null -w "%{http_code}\n" "https://cloudprice.net/volcengine/ecs"   # 404
curl -sL "https://keeper.sparecores.net/servers" -o /tmp/sc.json -w "%{http_code} %{size_download}\n"  # 200 74770
python3 -c "import json;d=json.load(open('/tmp/sc.json'));print(sorted({s.get('vendor') for s in d}))"
# ['Alibaba Cloud', 'Amazon Web Services', 'Google Cloud Platform']   ← 无 volcengine
```

- `cloudprice.net`：导航仅 `/aws/*`、`/gcp/*`；`/volcengine/`、`/volcengine/ecs` → 404；
  `/models/providers` 里的 ByteDance/Volc 是 **LLM 模型供应商**（豆包），非计算实例
- `vantage.sh`、`cloud-gpus.com` → 200 但无 volcengine；`getdeploying.com` → 403
- `pricing.api.infracost.io` → 403 Invalid API key（前序一次 POST 探测，已停）

### H. GitHub 价格仓库

- 仅 `YtYEven/volcengine-pricing-quote-skills`（0 star）：README 说明依赖 **Playwright 浏览器自动化登录官网下载 CSV**，
  **非匿名 JSON**，仓库内只有 README/LICENSE/.gitignore
- `galong/volcengine-ecs-deploy`、`terraform-volcenginecc-*`、`itswl/PyVolcEngine` → 无机型价
- GitHub code search API → 401（未授权不可用）

### I. CDN 静态资源（200，但只有站点配置与 CSS 类名）

- `portal.volccdn.com/.../main.fa8cf380.js`（4.3 MB）及 chunk `1906/6166/4094/726.js` → 200，
  仅含 CSS 类名（`price-divider_*` 等）与 `/api/bee/getJson` CMS 调用，**无价格 API**
- `lf3-beecdn.bytetos.com/.../bee_prod_950_bee_publish_*.json` → 200，均为站点配置（footerConfig 等）
- `res.gcloudcache.com/volc-fe/www-arch/btminfo/volcengine_www_product.json` → 200，仅路由映射表

### J. Wayback / 移动站（本轮新增确认，均为负）

```bash
curl -sL "http://archive.org/wayback/available?url=www.volcengine.com/product/ecs/pricing"
# {"url": "...", "archived_snapshots": {}}      ← 无任何历史快照，不存在老版静态表格可挖
curl -sL -o /dev/null -w "%{http_code}\n" https://m.volcengine.com/product/ecs/pricing
# 000                                          ← 无此主机
```

### K. 搜索引擎发现受阻

Bing 返回地理错位结果；DuckDuckGo html/lite → 202 反爬；Mojeek → 200 但无有效结果。

---

## 三、四档机型覆盖结果

| 档位 | 能否取到 CNY/hr | 说明 |
|---|---|---|
| 2C4G | ❌ | 全网无可解析单价 |
| 2C8G | ❌ | 同上 |
| 4C16G | ❌ | 同上 |
| 8C32G | ❌ | 同上 |

**四档全部无法对应。** 火山引擎机型命名（如 `ecs.g3i.large` 等）在匿名可达页面中均未与价格同时出现。

---

## 四、建议

1. `bench.py` 中将火山引擎 ECS 标注为「无匿名按量价」；跨云比价表该列留空或标注 N/A，避免填入估算值造成误导。
2. 若必须接入：
   - 正式路径：申请火山引擎 AK/SK，调用 OpenAPI 询价（`DescribePrice` 类接口），只读、不建资源；
   - 临时路径：人工从价格计算器/控制台抄录四档单价，写入本地 `clouds.yaml` 静态价格表并注明采集日期与口径。
3. 零凭据旁路已穷尽（官网/计算器/文档/CDN/国际站/第三方聚合/GitHub/Wayback/移动站/DNS 变体共 11 类），不建议再投入探测。
