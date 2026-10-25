#!/usr/bin/env python3
"""hermes_relay.py - Siri快捷指令→Hermes(直连OCI, 国内走CF隧道)
接收: POST /ask {"q":"问题"}  或 GET /ask?q=问题
处理: 用 OpenRouter 免费模型 (OpenAI兼容, 无nous的tags限制)
返回: {"answer":"回复文本"}
不依赖Telegram, 同步返回, 国内iPhone走CF隧道到OCI即可。

部署: systemd tg-relay.service (ExecStart 用 venv python 绝对路径)
依赖: fastapi httpx dotenv uvicorn openai (在 /home/ubuntu/.hermes/hermes-install/venv)
"""
import os
from dotenv import dotenv_values
from fastapi import FastAPI, Request
from openai import OpenAI

ENV = dotenv_values("/home/ubuntu/.hermes/.env")
OR_KEY = ENV.get("OPENROUTER_API_KEY", "")
client = OpenAI(api_key=OR_KEY, base_url="https://openrouter.ai/api/v1")

# 用免费模型(先 curl 探可用: nemotron-3.5-lightning:free / north-mini-code:free)
MODEL = "nvidia/nemotron-3.5-lightning:free"

app = FastAPI()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/ask")
@app.get("/ask")
async def ask(request: Request):
    if request.method == "POST":
        try:
            data = await request.json()
            q = data.get("q", "")
        except Exception:
            q = ""
    else:
        q = request.query_params.get("q", "")
    if not q:
        return {"answer": "(空问题)"}
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "你是 Hermes，用户的 AI 助手，简洁直接回答中文问题。"},
                {"role": "user", "content": q},
            ],
            max_tokens=800,
            temperature=0.7,
            extra_headers={"HTTP-Referer": "https://hermes.local", "X-Title": "Hermes Relay"},
        )
        ans = resp.choices[0].message.content
    except Exception as e:
        ans = f"(调用失败: {e})"
    return {"answer": ans}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8099)
