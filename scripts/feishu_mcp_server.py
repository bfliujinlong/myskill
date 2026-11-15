#!/usr/bin/env python3
"""
Minimal stdio MCP server that proxies to remote feishu MCP.
Handles JSON-RPC 2.0 over stdin/stdout, compatible with Hermes native MCP client.
"""
import asyncio, json, sys, time
from pathlib import Path
import httpx

MCP_URL = "https://mcp.feishu.cn/mcp"
CREDS_PATH = "/home/ubuntu/.feishu/credentials.json"
ALLOWED_TOOLS = "search-doc,fetch-doc,create-doc,update-doc,list-docs,get-comments,add-comments,search-user,get-user,fetch-file"

def get_tat():
    creds = json.loads(Path(CREDS_PATH).read_text())
    r = httpx.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": creds["app_id"], "app_secret": creds["app_secret"]},
        timeout=10
    )
    d = r.json()
    return d["tenant_access_token"]

def remote_call(method, params=None):
    """Returns the result payload (not the JSON-RPC envelope)."""
    tat = get_tat()
    payload = {"jsonrpc": "2.0", "id": int(time.time()*1000) % 1000000, "method": method}
    if params: payload["params"] = params
    r = httpx.post(MCP_URL, headers={
        "X-Lark-MCP-TAT": tat,
        "X-Lark-MCP-Allowed-Tools": ALLOWED_TOOLS,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }, json=payload, timeout=120)
    text = r.text.strip()
    if text.startswith("data:"):
        for line in text.split("\n"):
            if line.strip().startswith("data:"):
                text = line.strip()[5:].strip()
                break
    resp = json.loads(text)
    if "error" in resp:
        raise Exception(f"MCP error: {resp['error']}")
    return resp.get("result", {})

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        req = json.loads(line)
        method = req.get("method", "")
        req_id = req.get("id")
        params = req.get("params")
        
        if method == "initialize":
            resp = {"jsonrpc":"2.0","id":req_id,"result":{
                "protocolVersion":"2024-11-05",
                "capabilities":{"tools":{}},
                "serverInfo":{"name":"feishu-mcp-proxy","version":"1.0.0"}
            }}
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            try:
                result = remote_call("tools/list")
                tools = result.get("tools", [])
                resp = {"jsonrpc":"2.0","id":req_id,"result":{"tools":tools}}
            except Exception as e:
                resp = {"jsonrpc":"2.0","id":req_id,"error":{"code":-32603,"message":str(e)}}
        elif method == "tools/call":
            try:
                result = remote_call("tools/call", params)
                content = result.get("content", [])
                for c in content:
                    if c.get("type") == "text" and not isinstance(c.get("text"), str):
                        c["text"] = json.dumps(c["text"], ensure_ascii=False)
                resp = {"jsonrpc":"2.0","id":req_id,"result":{"content":content}}
            except Exception as e:
                resp = {"jsonrpc":"2.0","id":req_id,"error":{"code":-32603,"message":str(e)}}
        else:
            resp = {"jsonrpc":"2.0","id":req_id,"error":{"code":-32601,"message":f"Method not found: {method}"}}
        
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
