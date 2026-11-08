#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业微信群机器人 Webhook 推送中继 (纯标准库, 零依赖, 零费用)
仅出站访问 qyapi.weixin.qq.com, 不需要公网 IP / 入站端口。
接收 Alertmanager {alerts:[...]} POST, 过滤 P0, 去重, 渲染 markdown 并 @人。

用法:
  # HTTP 服务 (默认 :9100/alert) 接 Alertmanager
  WECOM_WEBHOOK_KEY=xxxx WECOM_P0_AT_USERIDS=zhangsan,lisi python3 wecom_webhook_relay.py
  # 发测试卡片
  python3 wecom_webhook_relay.py --test
安全: webhook key 只读环境变量; 等同发消息权限, 须保密 [REDACTED]。
"""
import os, sys, json, time, hashlib
import urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

WECOM_API = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send"
RATE_LIMIT_PER_MIN = 20
DEDUP_TTL = 600
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = int(os.getenv("RELAY_PORT", "9100"))


def get_webhook_key():
    for i, a in enumerate(sys.argv):
        if a == "--key" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return os.getenv("WECOM_WEBHOOK_KEY", "")


def get_at_userids():
    return [u.strip() for u in os.getenv("WECOM_P0_AT_USERIDS", "").split(",") if u.strip()]


def get_at_mobiles():
    return [m.strip() for m in os.getenv("WECOM_P0_AT_MOBILES", "").split(",") if m.strip()]


_sent_cache = {}


def fingerprint(alert):
    labels = alert.get("labels", {})
    parts = labels.get("alertname", "") + labels.get("instance", "") + labels.get("job", "")
    return hashlib.md5(parts.encode("utf-8")).hexdigest()


def is_p0(alert):
    labels = alert.get("labels", {})
    sev = (labels.get("severity") or "").lower()
    pri = (labels.get("priority") or "").upper()
    return sev == "critical" or pri == "P0"


def render_markdown(alert):
    labels = alert.get("labels", {})
    annotations = alert.get("annotations", {})
    name = labels.get("alertname", "未知告警")
    instance = labels.get("instance", labels.get("host", "N/A"))
    severity = labels.get("severity", labels.get("priority", "P0"))
    summary = annotations.get("summary", annotations.get("description", "无附加说明"))
    starts = alert.get("startsAt", "")[:19].replace("T", " ")
    at = ""
    u = get_at_userids()
    m = get_at_mobiles()
    if u:
        at += " ".join("<@%s>" % x for x in u)
    if m:
        at += " ".join("@%s" % x for x in m)
    lines = [
        '## ⚠️ [P0 告警] <font color="warning">%s</font>' % name,
        "> **级别**：%s" % severity,
        "> **实例**：%s" % instance,
        "> **说明**：%s" % summary,
    ]
    if starts:
        lines.append("> **触发**：%s" % starts)
    if at:
        lines.append("\n请 %s 立即跟进" % at)
    return "\n".join(lines)


def send_to_wecom(md):
    key = get_webhook_key()
    if not key:
        print("[WARN] 未配置 WECOM_WEBHOOK_KEY，跳过推送", file=sys.stderr)
        return False
    url = "%s?key=%s" % (WECOM_API, key)
    payload = json.dumps({"msgtype": "markdown", "markdown": {"content": md}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("errcode") == 0:
                print("[OK] 推送成功")
                return True
            print("[ERR] 企微返回:", body, file=sys.stderr)
            return False
    except urllib.error.URLError as e:
        print("[ERR] 推送失败:", e, file=sys.stderr)
        return False


def handle_alertmanager_payload(payload):
    alerts = payload.get("alerts", [])
    pushed = 0
    now = time.time()
    for alert in alerts:
        if alert.get("status", "firing") != "firing":
            continue
        if not is_p0(alert):
            continue
        fp = fingerprint(alert)
        if fp in _sent_cache and now - _sent_cache[fp] < DEDUP_TTL:
            print("[SKIP] 去重: %s" % fp)
            continue
        if send_to_wecom(render_markdown(alert)):
            _sent_cache[fp] = now
            pushed += 1
    expired = [k for k, v in _sent_cache.items() if now - v >= DEDUP_TTL]
    for k in expired:
        del _sent_cache[k]
    return pushed


class Handler(BaseHTTPRequestHandler):
    def _respond(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": msg}).encode("utf-8"))

    def do_POST(self):
        if self.path.rstrip("/") not in ("/alert", "/webhook"):
            self._respond(404, "not found")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
        except Exception as e:
            self._respond(400, "bad json: %s" % e)
            return
        self._respond(200, "pushed=%d" % handle_alertmanager_payload(payload))

    def do_GET(self):
        if self.path == "/healthz":
            self._respond(200, "alive")
        else:
            self._respond(404, "not found")

    def log_message(self, format, *args):
        sys.stderr.write("[relay] " + (format % args) + "\n")


def send_test():
    sample = {"alerts": [{
        "status": "firing",
        "labels": {"alertname": "示例P0告警", "severity": "critical", "instance": "app-prod-01", "job": "demo"},
        "annotations": {"summary": "这是一条测试 P0 告警"},
        "startsAt": "2026-01-01T10:00:00+08:00"
    }]}
    print("测试推送结果: pushed=%d" % handle_alertmanager_payload(sample))


def main():
    if "--test" in sys.argv:
        send_test()
        return
    print("企业微信 P0 中继启动: http://%s:%d/alert (仅出站)" % (LISTEN_HOST, LISTEN_PORT))
    if not get_webhook_key():
        print("[WARN] WECOM_WEBHOOK_KEY 未设置", file=sys.stderr)
    ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
