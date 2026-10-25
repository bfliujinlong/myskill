#!/usr/bin/env python3
"""cc2azure.py - minimal Anthropic->Azure OpenAI translation proxy for Claude Code.
Listen :4000, translate /v1/messages (Anthropic) -> Azure chat/completions.
Key read at request time from NOTE (never hardcoded). Deployment name = DEPLOY.
Verified: curl POST /v1/messages returns correct Claude-style Message JSON.
KNOWN GAP: cc itself sends streaming requests; add SSE (data: {json}\\n\\n ... [DONE])
before cc will accept it. See SKILL.md Path B.
"""
import os, json, urllib.request
from fastapi import FastAPI, Request, Response

NOTE = "/home/note.txt"   # user-stored credential file; override via env CC2AZURE_NOTE
DEPLOY = os.environ.get("CC2AZURE_DEPLOY", "gpt-5-mini")

def load_cred():
    p = os.environ.get("CC2AZURE_NOTE", NOTE)
    lines = [l.strip() for l in open(p) if l.strip()]
    endpoint = [l for l in lines if l.startswith("https")][0].rstrip("/")
    key = [l for l in lines if len(l) == 84 and " " not in l][0]
    return endpoint, key

app = FastAPI()

@app.post("/v1/messages")
async def messages(req: Request):
    body = await req.json()
    endpoint, key = load_cred()
    sys_msg = ""
    msgs = []
    for m in body.get("messages", []):
        role = m["role"]
        if role == "system":
            sys_msg = m["content"]; continue
        content = m["content"]
        if isinstance(content, list):
            text = "".join(p.get("text", "") for p in content if p.get("type") == "text")
        else:
            text = str(content)
        msgs.append({"role": role, "content": text})
    if sys_msg:
        msgs.insert(0, {"role": "system", "content": sys_msg})
    max_tokens = body.get("max_tokens", body.get("max_completion_tokens", 1024))
    payload = {"messages": msgs, "max_completion_tokens": max_tokens}
    url = f"{endpoint}/openai/deployments/{DEPLOY}/chat/completions?api-version=2024-06-01"
    data = json.dumps(payload).encode()
    r = urllib.request.Request(url, data=data,
                               headers={"api-key": key, "Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(r, timeout=120)
        d = json.loads(resp.read())
        text = d["choices"][0]["message"]["content"]
        return Response(content=json.dumps({
            "id": "msg_proxy", "type": "message", "role": "assistant",
            "model": DEPLOY, "stop_reason": "end_turn",
            "content": [{"type": "text", "text": text}]
        }), media_type="application/json")
    except urllib.error.HTTPError as e:
        return Response(content=e.read(), status_code=e.code, media_type="application/json")

@app.get("/health")
async def health():
    return {"ok": True}
