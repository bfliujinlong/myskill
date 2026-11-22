#!/usr/bin/env python3
"""Call a feishu MCP tool by name with JSON args."""
import sys, json, time
import httpx
from pathlib import Path

CREDS_PATH = "/home/ubuntu/.feishu/credentials.json"
MCP_URL = "https://mcp.feishu.cn/mcp"

def get_tat():
    creds = json.loads(Path(CREDS_PATH).read_text())
    r = httpx.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": creds["app_id"], "app_secret": creds["app_secret"]},
        timeout=10
    )
    d = r.json()
    if d.get("code") != 0:
        raise Exception(f"TAT failed: {d}")
    return d["tenant_access_token"]

def main():
    if len(sys.argv) < 2:
        print("Usage: feishu_mcp_call.py <tool-name> '<json-args>'")
        print("Available tools: search-doc, fetch-doc, create-doc, update-doc, list-docs, get-comments, add-comments, search-user, get-user, fetch-file")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    tat = get_tat()
    
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time()*1000) % 1000000,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": args}
    }
    
    r = httpx.post(
        MCP_URL,
        headers={
            "X-Lark-MCP-TAT": tat,
            "X-Lark-MCP-Allowed-Tools": tool_name,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        json=payload,
        timeout=120,
    )
    
    if r.status_code != 200:
        print(json.dumps({"error": f"HTTP {r.status_code}", "body": r.text[:500]}))
        sys.exit(1)
    
    # Parse response (may be JSON or SSE)
    resp_text = r.text.strip()
    if resp_text.startswith("data: "):
        resp_text = resp_text.split("\n")[0].replace("data: ", "")
    
    resp = json.loads(resp_text)
    
    if "error" in resp:
        print(json.dumps(resp["error"], ensure_ascii=False, indent=2))
        sys.exit(1)
    
    result = resp.get("result", {})
    content = result.get("content", [])
    
    for item in content:
        if item.get("type") == "text":
            # Try to parse as JSON for pretty output
            try:
                data = json.loads(item["text"])
                if isinstance(data, dict) and data.get("error"):
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(data, ensure_ascii=False, indent=2))
            except:
                print(item["text"])
        elif item.get("type") == "resource":
            print(json.dumps(item.get("resource", {}), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
