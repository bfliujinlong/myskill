"""阿里云 ECS 询价适配器 —— 需 AK，凭据来自 ~/.aliyun/config.json（不在代码/配置里落明文）。

实测可用：DescribePrice 返回 PriceInfo.Price（Currency=CNY，DetailInfo 含 instanceType/systemDisk/bandwidth 分项）。
"""
import json
import os
import sys

VENV = "/home/ubuntu/.hermes/cloud-mcp-venvs/alicloud/lib/python3.12/site-packages"
CRED = os.path.expanduser("~/.aliyun/config.json")
DEFAULT_REGION = "cn-hangzhou"


if VENV not in sys.path:
    sys.path.insert(0, VENV)


def _load_cred() -> dict:
    d = json.load(open(CRED))
    cur = d.get("current_profile")
    return next((p for p in d.get("profiles", []) if p.get("name") == cur), d["profiles"][0])


def _client(region: str):
    from alibabacloud_tea_openapi import models as o
    from alibabacloud_ecs20140526.client import Client
    p = _load_cred()
    cfg = o.Config(access_key_id=p["access_key_id"], access_key_secret=p["access_key_secret"])
    cfg.endpoint = f"ecs.{region}.aliyuncs.com"
    return Client(cfg)


def query(instance_type: str, region: str = DEFAULT_REGION,
          price_unit: str = "Hour") -> dict:
    """返回 {'currency','total','instance','systemDisk','bandwidth'}。

    price_unit: Hour / Month / Year。Hour 对应按量付费。
    """
    from alibabacloud_ecs20140526 import models as e
    c = _client(region)
    req = e.DescribePriceRequest(region_id=region, instance_type=instance_type,
                                 price_unit=price_unit, resource_type="instance")
    body = c.describe_price(req).body
    info = body.price_info.to_map().get("Price", {})

    def _pick(name):
        for d in info.get("DetailInfos", {}).get("DetailInfo", []):
            if d.get("Resource") == name:
                return d.get("TradePrice")
        return None

    return {
        "instanceType": instance_type,
        "region": region,
        "currency": info.get("Currency"),
        "unit": price_unit,
        "total": info.get("TradePrice"),
        "originalTotal": info.get("OriginalPrice"),
        "instance": _pick("instanceType"),
        "systemDisk": _pick("systemDisk"),
        "bandwidth": _pick("bandwidth"),
    }
