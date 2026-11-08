"""腾讯云 CVM 按需询价适配器 —— 需要 SecretId/SecretKey。

数据源：CVM 官方 OpenAPI `InquiryPriceRunInstances`（POSTPAID_BY_HOUR）。
凭据链（SDK DefaultCredentialProvider）：环境变量 → ~/.tencentcloud/credentials → 实例角色。
凭据缺失时抛出带指引的 CredentialError，不静默返回空价。
"""
import os

CRED_ENV = ("TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY")
CRED_FILE = os.path.expanduser("~/.tencentcloud/credentials")


class CredentialError(RuntimeError):
    pass


def _cred():
    """取凭据：优先环境变量，再 ~/.tencentcloud/credentials 的 [default] 段。"""
    sid = os.environ.get(CRED_ENV[0])
    sk = os.environ.get(CRED_ENV[1])
    if sid and sk:
        return sid, sk, os.environ.get("TENCENTCLOUD_TOKEN")
    if os.path.isfile(CRED_FILE):
        import configparser
        cp = configparser.ConfigParser()
        cp.read(CRED_FILE)
        sec = cp["default"] if cp.has_section("default") else None
        if sec:
            sid = sec.get("secret_id") or sec.get("secret-id")
            sk = sec.get("secret_key") or sec.get("secret-key")
            if sid and sk:
                return sid, sk, sec.get("token")
    raise CredentialError(
        "腾讯云凭据缺失。二选一：\n"
        "  1) export TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY（+可选 TENCENTCLOUD_TOKEN）\n"
        f"  2) 写 {CRED_FILE}（chmod 600）的 [default] 段 secret_id / secret_key\n"
        "详见 CREDENTIALS.md §2"
    )


def query(instance_type: str, region: str = "ap-guangzhou", zone: str = "") -> dict:
    """按量后付费询价。返回 {'total': USD/hr, 'cny_hr': 元/小时, 'instanceType': ...}。

    口径对齐其它云：Linux、按量后付费、单机、无数据盘、公网按流量不计入。
    """
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.cvm.v20170312 import cvm_client, models

    sid, sk, token = _cred()
    cred = credential.Credential(sid, sk, token) if token else credential.Credential(sid, sk)

    hp = HttpProfile(endpoint="cvm.tencentcloudapi.com")
    cp = ClientProfile(httpProfile=hp)
    cli = cvm_client.CvmClient(cred, region, cp)

    # 镜像不硬编码：公共镜像 ID 随地域/时间变化，写死必然失效。
    # 用 DescribeImages 动态取该地域的公共 Linux 镜像（CentOS/TencentOS 优先）。
    image_id = _public_linux_image(cli, region)

    req = models.InquiryPriceRunInstancesRequest()
    params = {
        "InstanceChargeType": "POSTPAID_BY_HOUR",
        "InstanceCount": 1,
        "Placement": {"Zone": zone or f"{region}-3"},
        "InstanceType": instance_type,
        "ImageId": image_id,
    }
    req.from_json_string(__import__("json").dumps(params))
    resp = cli.InquiryPriceRunInstances(req)

    price = resp.Price.InstancePrice
    cny = float(price.UnitPrice)
    if getattr(price, "ChargeUnit", "HOUR") != "HOUR":
        raise ValueError(f"口径不一致：返回计价单位 {price.ChargeUnit}，未按小时")
    return {
        "instanceType": instance_type,
        "cny_hr": cny,
        "total": cny / _usd_cny(),
        "currency": "USD",
        "chargeUnit": "HOUR",
    }


def _usd_cny() -> float:
    """CNY→USD 汇率。优先环境变量 USD_CNY，否则取公开汇率，失败则用保守值。"""
    v = os.environ.get("USD_CNY")
    if v:
        return float(v)
    try:
        import json
        import urllib.request
        with urllib.request.urlopen(
            "https://api.exchangerate-api.com/v4/latest/USD", timeout=15
        ) as r:
            return float(json.loads(r.read())["rates"]["CNY"])
    except Exception:
        return 7.25  # 保守兜底，并在返回中标注


def _public_linux_image(cli, region: str) -> str:
    """取该地域一个可用的公共 Linux 镜像 ID（CentOS/TencentOS 优先，退回任意公共 Linux）。

    硬编码镜像 ID 会随地域和下线失效，故每次动态取。取不到就抛错，不静默用假值。
    """
    from tencentcloud.cvm.v20170312 import models as m

    req = m.DescribeImagesRequest()
    req.from_json_string(__import__("json").dumps({
        "Filters": [{"Name": "image-type", "Values": ["PUBLIC_IMAGE"]},
                    {"Name": "platform", "Values": ["Linux"]}],
        "Limit": 100,
    }))
    resp = cli.DescribeImages(req)
    imgs = list(resp.ImageSet or [])
    if not imgs:
        raise ValueError(f"地域 {region} 未取到公共 Linux 镜像，无法询价")

    # 优先 TencentOS / CentOS，避免 Ubuntu/Debian 某些机型缺驱动
    for prefer in ("TencentOS", "CentOS"):
        for im in imgs:
            if prefer.lower() in (im.ImageName or "").lower():
                return im.ImageId
    return imgs[0].ImageId
