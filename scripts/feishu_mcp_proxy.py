#!/usr/bin/env python3
"""Local stdio MCP proxy that forwards calls to remote feishu MCP with TAT auth."""
import asyncio, json, os, sys, time
from pathlib import Path
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.client.streamable_http import streamable_http_client

MCP_URL = "https://mcp.feishu.cn/mcp"
CREDS_PATH = "/home/ubuntu/.feishu/credentials.json"

def get_tat():
    """Get fresh tenant access token."""
    creds = json.loads(Path(CREDS_PATH).read_text())
    r = httpx.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": creds["app_id"], "app_secret": creds["app_secret"]},
        timeout=10
    )
    data = r.json()
    if data.get("code") != 0:
        raise Exception(f"TAT failed: {data}")
    return data["tenant_access_token"]

server = Server("feishu-mcp-proxy")

@server.list_tools()
async def list_tools():
    """Forward tools/list to remote feishu MCP."""
    tat = get_tat()
    async with streamable_http_client(
        MCP_URL,
        headers={"X-Lark-MCP-TAT": tat, "X-Lark-MCP-Allowed-Tools": "search-doc,fetch-doc,create-doc,update-doc,list-docs,get-comments,add-comments,search-user,get-user,fetch-file"},
        timeout=120,
    ) as (read, write, _):
        from mcp.types import ListToolsRequest, ListToolsResult
        req = ListToolsRequest(method="tools/list")
        await write.write(req.model_dump_json())
        resp_json = await read.read()
        result = ListToolsResult.model_validate_json(resp_json)
        return result.tools or []

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Forward tools/call to remote feishu MCP."""
    tat = get_tat()
    async with streamable_http_client(
        MCP_URL,
        headers={"X-Lark-MCP-TAT": tat, "X-Lark-MCP-Allowed-Tools": "search-doc,fetch-doc,create-doc,update-doc,list-docs,get-comments,add-comments,search-user,get-user,fetch-file"},
        timeout=120,
    ) as (read, write, _):
        from mcp.types import CallToolRequest, CallToolResult
        req = CallToolRequest(method="tools/call", params={"name": name, "arguments": arguments})
        await write.write(req.model_dump_json())
        resp_json = await read.read()
        result = CallToolResult.model_validate_json(resp_json)
        return result.content

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
