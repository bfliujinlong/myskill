"""Azure Retail Prices API 适配器 —— 官方公开接口，完全匿名无需 auth。"""
import json
import urllib.parse
import urllib.request

ENDPOINT = "https://prices.azure.com/api/retail/prices"
UA = "Mozilla/5.0 (compatible; cloud-price-bench/1.0)"
DEFAULT_REGION = "eastus"


def query(sku_name: str = "", region: str = DEFAULT_REGION,
          service: str = "Virtual Machines", limit: int = 500) -> list:
    """返回 [{'skuName','retailPrice','unitOfMeasure','productName','meterName','region'}]。

    sku_name 支持精确匹配（如 'D2 v3'）；留空则列出该 region 全部。
    """
    filt = f"serviceName eq '{service}' and armRegionName eq '{region}'"
    if sku_name:
        filt += f" and skuName eq '{sku_name}'"
    url = f"{ENDPOINT}?{urllib.parse.urlencode({'$filter': filt})}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        d = json.loads(resp.read().decode("utf-8", errors="replace"))

    rows = []
    for i in d.get("Items", [])[:limit]:
        rows.append({
            "skuName": i.get("skuName"),
            "retailPrice": i.get("retailPrice"),
            "unitOfMeasure": i.get("unitOfMeasure"),
            "productName": i.get("productName"),
            "meterName": i.get("meterName"),
            "region": i.get("armRegionName"),
            "currency": i.get("currencyCode", "USD"),
        })
    return rows
