"""火山引擎 ECS 按需询价适配器 —— 需要 AccessKey/SecretKey。

数据源：`volcenginesdk-billing` 的 `QueryPriceForPayAsYouGo`（按需询价，非 DescribePrice）。
机型列表用 `volcenginesdk-ecs` 的 `DescribeInstanceTypes`。
凭据链：环境变量 → ~/.volcengine/config.json → ECS 实例角色。
"""
import json
import os

CRED_ENV = ("VOLCENGINE_ACCESS_KEY", "VOLCENGINE_SECRET_KEY")
CRED_FILE = os.path.expanduser("~/.volcengine/config.json")


class CredentialError(RuntimeError):
    pass


def _cred():
    ak = os.environ.get(CRED_ENV[0])
    sk = os.environ.get(CRED_ENV[1])
    if ak and sk:
        return ak, sk, os.environ.get("VOLCENGINE_SESSION_TOKEN"), \
            os.environ.get("VOLCENGINE_REGION", "cn-beijing")
    if os.path.isfile(CRED_FILE):
        d = json.load(open(CRED_FILE))
        prof = d.get("profiles", {}).get(d.get("current", "default"), {})
        ak = prof.get("access-key") or prof.get("access_key")
        sk = prof.get("secret-key") or prof.get("secret_key")
        if ak and sk:
            return ak, sk, prof.get("session-token"), prof.get("region", "cn-beijing")
    raise CredentialError(
        "火山引擎凭据缺失。二选一：\n"
        "  1) export VOLCENGINE_ACCESS_KEY / VOLCENGINE_SECRET_KEY\n"
        f"  2) 写 {CRED_FILE}（chmod 600），profiles.default 内 access-key / secret-key\n"
        "详见 CREDENTIALS.md §3"
    )


def query(instance_type: str, region: str = "cn-beijing") -> dict:
    """按量付费询价。返回 {'total': USD/hr, 'cny_hr': 元/小时, 'instanceType': ...}。

    注意：`QueryPriceForPayAsYouGo` 的 config_list 需要 product / charge_item_code /
    configuration_code / count / use_duration 枚举值。首次实调若枚举对不上，
    会抛 ConfigurationError 并打印 SDK 返回的合法值，便于校准，不静默吞错。
    """
    # 2026-11-01 拆 wheel 取证（volcenginesdk_billing 5.0.56）：
    #   API 类真名 BILLINGApi（不是 BillingService），方法 query_price_for_pay_as_you_go(body)
    #   config_list 字段：charge_item_code/configuration_code/count(str)/quantity(int)/use_duration(int)
    from volcenginesdkbilling import BILLINGApi
    from volcenginesdkbilling.models import (
        QueryPriceForPayAsYouGoRequest,
        ConfigListForQueryPriceForPayAsYouGoInput,
    )

    ak, sk, token, region = _cred()
    svc = BILLINGApi()
    svc.set_ak(ak)
    svc.set_sk(sk)
    if token:
        svc.set_session_token(token)
    svc.set_region(region)

    req = QueryPriceForPayAsYouGoRequest(
        product="ecs",
        config_list=[ConfigListForQueryPriceForPayAsYouGoInput(
            charge_item_code="instance",
            configuration_code=instance_type,
            count="1",
            quantity=1,
            use_duration=1,
        )],
    )
    resp = svc.query_price_for_pay_as_you_go(req)
    if not getattr(resp, "config_list", None):
        raise RuntimeError(
            f"火山询价返回空 config_list（机型 {instance_type}）。"
            "多为 configuration_code 枚举值不匹配，请用 DescribeInstanceTypes 校准。"
        )
    cny = float(resp.total_original_amount)
    return {
        "instanceType": instance_type,
        "cny_hr": cny,
        "total": cny / _usd_cny(),
        "currency": getattr(resp, "currency", "CNY"),
        "chargeUnit": "HOUR",
    }


def _usd_cny() -> float:
    v = os.environ.get("USD_CNY")
    if v:
        return float(v)
    try:
        import urllib.request
        with urllib.request.urlopen(
            "https://api.exchangerate-api.com/v4/latest/USD", timeout=15
        ) as r:
            return float(json.loads(r.read())["rates"]["CNY"])
    except Exception:
        return 7.25
