#!/usr/bin/env python3
"""Codex <-> litellm 之间的极简反向代理。
Codex 强制发 namespace 等非标准 tool, nous 免费模型拒收 -> 400。
此代理在转发前剥掉非 {function,web_search,x_search} 的 tool, 再转给 litellm (:4100)。
Codex 的 WS 升级 -> 本代理不处理 WS, 返回 403 让 Codex 降级 HTTPS (litellm WS 不兼容)。
"""
import json, urllib.request, http.server, socketserver

UPSTREAM = "http://127.0.0.1:4100"
# Codex 自己处理 agentic 工具(写文件/跑命令), 模型只需输出文本/代码。
# 因此直接剥掉所有 tools (免费模型不支持 namespace/web_search/x_search 等类型)
def strip_tools(obj):
    if isinstance(obj, dict):
        if "tools" in obj:
            obj["tools"] = []
        for k, v in list(obj.items()):
            obj[k] = strip_tools(v)
    elif isinstance(obj, list):
        return [strip_tools(x) for x in obj]
    return obj


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _forward(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        try:
            data = json.loads(body) if body else {}
            data = strip_tools(data)
            body2 = json.dumps(data).encode()
        except Exception:
            body2 = body
        req = urllib.request.Request(UPSTREAM + self.path, data=body2,
                                     headers={"Content-Type": "application/json"})
        try:
            resp = urllib.request.urlopen(req, timeout=90)
            payload = resp.read()
            self.send_response(resp.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except urllib.error.HTTPError as e:
            payload = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def do_POST(self):
        if "responses" in self.path or "chat/completions" in self.path:
            self._forward()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):
        pass


class ReuseTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with ReuseTCPServer(("127.0.0.1", 4101), H) as srv:
        srv.serve_forever()
