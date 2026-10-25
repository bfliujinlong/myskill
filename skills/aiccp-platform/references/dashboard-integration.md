# Dashboard 云资源集成

## 后端：纯 Python OpenAPI 调用（无 SDK/CLI 依赖）

容器内 pip 超时，CLI 跨架构 SIGSEGV，故用 httpx 直签 OpenAPI。

```python
# 签名骨架
def _sign(params, method="GET"):
    sorted_params = sorted(params.items())
    query = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
    string_to_sign = f"{method}&{urllib.parse.quote('/', safe='')}&{urllib.parse.quote(query, safe='')}"
    h = hmac.new((sk + "&").encode(), string_to_sign.encode(), hashlib.sha1)
    return base64.b64encode(h.digest()).decode()
```

- AK/SK 从 `~/.aliyun/config.json` profiles[0] 读取
- 必须先 `docker cp /root/.aliyun aicc-backend:/root/.aliyun`
- 内存缓存 `_cache` + `_cache_ts`，TTL=600s

## API 路由

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/v1/cloud-resources/summary` | GET | 汇总（实例数/CPU/内存/费用） |
| `/api/v1/cloud-resources/instances` | GET | 实例列表 |
| `/api/v1/cloud-resources/billing` | GET | 本月账单 |

注册 router：在 `/app/app/api/__init__.py` 加 `from app.api.cloud_resource import router as cloud_resource_router` + `api_router.include_router(cloud_resource_router)`。

## 前端注入（nginx sub_filter）

```nginx
gzip off;
sub_filter "</head>" "<link rel='stylesheet' href='/mobile-responsive.css'><script src='/cloud-resource.js' defer></script></head>";
sub_filter_once on;
sub_filter_types text/html;
```

JS 文件放在 `/usr/share/nginx/html/cloud-resource.js`，内容：检测 `location.pathname.includes('/dashboard')` 后 fetch API 并渲染卡片（实例总数/运行中/vCPU/内存/本月费用 + 实例表格）。

## 验证

```bash
# API
ssh ali 'docker exec aicc-backend curl -sS http://127.0.0.1:8000/api/v1/cloud-resources/summary' | python3 -m json.tool

# 外网
curl http://139.196.171.8/api/v1/cloud-resources/summary
curl http://139.196.171.8/cloud-resource.js  # 应返回 200
```

## 扩展新云

同样的模式：新 Service 类 + API router + 前端 JS。OCI/GCP 用各自的 REST API 签名方式，架构一致。
