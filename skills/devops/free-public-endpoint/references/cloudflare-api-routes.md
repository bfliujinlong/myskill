# Cloudflare API 路由管理

Token-based named tunnel（`cfut_...` 格式）的 ingress 由 CF API 管理，本地 config.yml 只声明 tunnel id，CF 边缘会拉取 API 配置。

## API 端点
```
GET  /client/v4/accounts/{account_id}/cfd_tunnel
PUT  /client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations
GET  /client/v4/zones/{zone_id}/dns_records
POST /client/v4/zones/{zone_id}/dns_records
```

## 鉴权
- X-Auth-Key: Global API Key (cfk_ 开头)
- X-Auth-Email: 账号邮箱

## 鉴权坑：API Token vs Global Key 权限不同
- **API Token**（`cfut_` 开头）：权限由创建时勾选决定，常见只有 `#zone:read`（只读），**无法读写 DNS 记录**。报 `Authentication error (code 10000)` 或 `Unauthorized (code 9109)` 时先检查 token 权限。
- **Global Key**（`cfk_` 开头）：拥有账号全部权限，但必须配对正确的 `X-Auth-Email`。报 `Authentication failed (status 400, code 9106)` 说明邮箱不匹配——Global Key 绑定的是创建时的账号邮箱，换邮箱后旧 key 失效。
- **排查顺序**：① 确认 key 类型（cfut_=API Token / cfk_=Global Key）→ ② Global Key 必须配创建时的账号邮箱 → ③ API Token 检查 permissions 是否含 `#dns_records:edit` → ④ 两者都失败则走浏览器登录 CF 控制台手动操作。

## 添加新子域 A 记录（非隧道场景）
当用户要求把一个新子域指向一个新 IP（如 `aicc.example.com → 1.2.3.4`），用 Global Key：
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
  -H "X-Auth-Key: {global_key}" -H "X-Auth-Email: {email}" \
  -H "Content-Type: application/json" \
  -d '{"type":"A","name":"aicc","content":"1.2.3.4","ttl":1,"proxied":false}'
```
- `proxied:false` = DNS only（灰色云），直接解析到源站 IP
- `proxied:true` = 走 CF 代理（橙色云），隐藏源站 IP
- 新阿里云 VM 的 A 记录通常用 `proxied:false`（直接暴露 IP）

## 添加 CNAME 根域名指向隧道
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
  -H "X-Auth-Key: {global_key}" -H "X-Auth-Email: {email}" \
  -d '{"type":"CNAME","name":"@","content":"<TUNNEL_ID>.cfargotunnel.com","proxied":true}'
```

## 添加隧道路由（决定 hostname 指向哪里）
```bash
curl -s -X PUT "https://api.cloudflare.com/client/v4/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations" \
  -H "X-Auth-Key: {global_key}" -H "X-Auth-Email: {email}" \
  -H "Content-Type: application/json" \
  -d '{"config":{"ingress":[{"hostname":"openmaic.example.com","service":"http://127.0.0.1:3000"},{"hostname":"dsh.example.com","service":"http://127.0.0.1:3081"},{"service":"http_status:404"}]}}'
```

## pitfalls
- token-based 隧道不要本地写 ingress 到 config.yml，会被 API 覆盖或冲突
- 修改 API 路由后需要 `systemctl restart cloudflared` 让边缘感知变更
- root 域名 (@) CNAME 只在 CF 支持 flattening CNAME 时生效（免费套餐已支持）