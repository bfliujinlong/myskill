# CF 隧道 + nginx 暴露 Hermes 中继的 nginx location 片段

## 前提
- cloudflared quick tunnel 已暴露 nginx:3080: `cloudflared tunnel --url http://127.0.0.1:3080`
- 中继服务 FastAPI 跑在 127.0.0.1:8099
- nginx 配置在 /etc/nginx/sites-enabled/dsh-combined (server { listen 3080 })

## 插入片段 (放在 server 块最后一个 } 之前)
```nginx
    # Hermes Siri 中继(快捷指令国内直连)
    location /relay/ {
        proxy_pass http://127.0.0.1:8099/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
```

## 插入方法 (python, 避免 sed 插错位置)
```python
p = "/etc/nginx/sites-enabled/dsh-combined"
s = open(p).read()
loc = '''
    location /relay/ {
        proxy_pass http://127.0.0.1:8099/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_read_timeout 60s;
    }
}
'''
idx = s.rfind("}")
s = s[:idx] + loc
open(p, "w").write(s)
```
# 然后:
sudo nginx -t && sudo systemctl reload nginx

## 验证公网可达
curl -s "https://<quick-tunnel-url>/relay/ask?q=hello"
# 期望: {"answer":"..."}

## 注意
- quick tunnel URL 重启会变 → 长期用 eu.org 域名 + 命名隧道固定 Public Hostname 路由
- DuckDNS 不可行(非 CF zone, 证书发不出)
