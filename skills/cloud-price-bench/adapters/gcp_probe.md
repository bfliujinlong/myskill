# GCP Compute Engine 价格探针（匿名 / 零凭据 / 免费）

探测日期：2026-10-31
约束：只读 GET，零花费，无账号注册，无信用卡，无 key/凭据。
目标：Linux 按量计价（on-demand）、USD/小时、us-central1 与 asia 区域、可取到 e2-standard-2/4/8。

---

## 结论速览

| 源 | 匿名可用 | 粒度 | 推荐度 |
|---|---|---|---|
| `gcloud-compute.com/<机型>.html` | ✅ | 单机型 × 全区域（含 on-demand + SUD） | ★★★ 首选（按区域取价） |
| `cloudprice.net/gcp/compute` | ✅ | 全机型 × 默认区域（us-central1） | ★★★ 首选（全机型一次拿全） |
| Google 官方 cloudbilling API | ❌ 403 | — | 无 key 不可用 |
| Google 官方页面 / JSON | ❌ 无内嵌数据 | — | 纯 JS 渲染 |
| infracost 官方 pricing API | ❌ 403 | — | 需 token |
| gstatic / cloudpricingcalculator | ❌ 404 | — | 已下线 |

---

## 一、可用端点

### 1. gcloud-compute.com —— 单机型详情页（含全区域单价）

- URL：`https://gcloud-compute.com/<machine-type>.html`
- 匿名 GET，无需 header 也可，建议带 UA。
- 页面内 HTML 表格按区域列出 **on-demand USD/hr** 与 **SUD 折后价**。

```bash
curl -sSL -A "Mozilla/5.0" "https://gcloud-compute.com/e2-standard-2.html"
```

解析（Python 提取表格行）：

```bash
python3 - <<'PY'
import re, urllib.request
url = "https://gcloud-compute.com/e2-standard-2.html"
h = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})).read().decode("utf-8","replace")
for r in re.findall(r'<tr[^>]*>(.*?)</tr>', h, re.S):
    c = [re.sub(r'\s+',' ', re.sub(r'<[^>]+>','',x)).strip()
         for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)]
    if c and c[0] in ("us-central1","asia-southeast1","asia-east1"):
        print(c[:6])   # [region, location, zone_count, ?, ondemand_USD_hr, SUD_USD_hr]
PY
```

实测返回（e2-standard-2）：

```
['us-central1',      'Iowa',      4, 4, '0.067',  '0.0402']
['asia-east1',       'Taiwan',    3, 4, '0.0776', '0.0361']
['asia-southeast1',  'Singapore', 3, 4, '0.0827', '0.0496']
```

实测返回（e2-standard-4）：

```
['us-central1',     'Iowa',      4, 4, '0.134',  '0.0804']
['asia-southeast1', 'Singapore', 3, 4, '0.1653', '0.0992']
```

e2-standard-2/4/8 全部可取 ✅（8 = 0.2680 us-central1 / 0.3307 asia-southeast1）

> 注：站内 `instances.html` 的 0.0809 是「全区域平均价（含 SUD）」，**不要**当作 us-central1 单价；按区域取价请用详情页。

### 2. cloudprice.net —— 全机型列表页（SSR，一次拿全）

- URL：`https://cloudprice.net/gcp/compute`
- 匿名 GET，200，约 574KB。数据在 HTML 内，**不是** JSON API，需正则解析内嵌数组。
- 默认区域为 us-central1（Iowa）；`?region=<region>` 会返回该区域单价。

```bash
curl -sSL -A "Mozilla/5.0" "https://cloudprice.net/gcp/compute"
```

解析：

```bash
python3 - <<'PY'
import re, urllib.request
def fetch(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})).read().decode("utf-8","replace")
h = fetch("https://cloudprice.net/gcp/compute")
for mt in ("e2-standard-2","e2-standard-4","e2-standard-8"):
    m = re.search(r'\\"%s\\",\\"%s\\",\\"[^\\]*\\",(\d+),(\d+),\\"([0-9.]+)\\"' % (mt, mt), h)
    print(mt, m.groups() if m else None)   # (vCPU, GB, USD/hr)
PY
```

实测返回（默认 us-central1）：

```
e2-standard-2  ('2', '8',  '0.0670')
e2-standard-4  ('4', '16', '0.1340')
e2-standard-8  ('8', '32', '0.2680')
```

切区域（`?region=asia-southeast1`，实测 200 且值变化）：

```bash
curl -sSL -A "Mozilla/5.0" "https://cloudprice.net/gcp/compute?region=asia-southeast1"
```

```
e2-standard-2  ('2', '8',  '0.0827')
e2-standard-4  ('4', '16', '0.1653')
e2-standard-8  ('8', '32', '0.3307')
```

**交叉验证**：两个源在 us-central1 与 asia-southeast1 的 e2-standard-2/4/8 单价完全一致 → 数据可信。

---

## 二、不可用端点及原因

| 端点 | 结果 | 原因 |
|---|---|---|
| `https://cloudbilling.googleapis.com/v1/services` | 403 | `Method doesn't allow unregistered callers`；需 API Key |
| `https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus` | 403 | 同上（Compute Engine service） |
| `https://cloud.google.com/compute/all-pricing` | 301 → `/products/compute/pricing` | 重定向 |
| `https://cloud.google.com/products/compute/pricing`（含 `?hl=en`） | 200 但无价格 | 2.2MB 纯 JS 渲染；`e2-standard` / `us-central1` 出现 0 次，无内嵌 JSON/CSV |
| `https://cloud.google.com/compute/pricing.json` 及同类 `/data/*.json`、`/_pwa/...` | 200 实为 404 壳 | SPA fallback，`<title>404. Page Not Found</title>` |
| `https://cloudbillingstorage.googleapis.com/` · `/pricelist.json` | 404 | 无公开 bucket listing |
| `https://www.gstatic.com/cloud-site/pricing/compute/pricelist.json` | 404 | 已下线 |
| `https://cloudpricingcalculator.appspot.com/static/data/pricelist.json`（及 5 种变体） | 404 | 静态端点已移除 |
| `https://pricing.api.infracost.io/graphql` | 403 | `Invalid API key` |
| `https://api.infracost.io/graphql` | 404 | 路径不存在 |
| `https://gcloud-compute.com/instances.json`（及 `/data/`、`/api/instances`） | 404 | 无 JSON API，只有 HTML |
| `https://cloudprice.net/api/*`、`/gcp/compute/instances/*.json` | 404 | 无 JSON API，数据内嵌于 SSR HTML |
| `https://api.vantage.sh/v1/providers/gcp/services` | 404 | — |
| `https://cloud.google.com/__/json/searchskus` | 400 | 内部端点，需参数+凭据 |
| `https://www.googleapis.com/bigquery/v2/projects/.../datasets` | 401 | BigQuery 需 OAuth |
| `https://api.github.com/search/code` | 401 | 需认证 |
| GitHub raw 镜像（terracost / opencost / kubecost gcp.json / gcloud-compute-pricing） | 404 | 路径不存在或仓库已变更；仅 infracost 源码 Go 文件可达（非价格数据） |
| `https://storage.googleapis.com/gcp-pricing/pricelist.json` | 403 | bucket 不公开 |

---

## 三、适配器建议（cloud-price-bench）

```python
# adapters/gcp.py
# 主源：gcloud-compute.com/<machine_type>.html  → 按区域 on-demand USD/hr（列索引 4）
# 备源：cloudprice.net/gcp/compute?region=<r>  → 全机型一次拉取（列索引 5）
# 两者交叉校验；仅用 GET，不落盘凭据。
```

- 需 Linux on-demand：gcloud-compute.com 第 5 列（0-based idx 4）为 on-demand，第 6 列为 SUD 折后价，**取 on-demand**。
- cloudprice.net 无独立 OS 维度，其默认即 Linux 通用型计价。
- 抓取节流：单机型页 ~67KB，全表页 ~574KB；建议缓存 + 每日一次刷新。
