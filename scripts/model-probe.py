#!/usr/bin/env python3
"""
model-probe.py - 全模型探测 + 分层路由 (v2, 2026-10-08)
每小时由 cron 调用。探测四层模型池，输出 model-rank.json 含 routing_policy：
  - simple 任务 → 本地 Ollama 优先 (deepseek-r1:1.5b > qwen3:4b > phi3.5:3.8b)
  - hard 任务   → Ali 百炼 qwen3.8-max (token-plan)
  - 云端免费池  → Mistral / OpenRouter (中间档兜底)
逻辑：
1. 并发探测各层模型（content 有值即 ok）
2. 排序写入 /data/model-probe/model-rank.json
3. routing_policy 给出 simple/hard/mid 三档当前最优
4. Ali 主力不可用时发 Telegram 告警
"""

import json, os, time, urllib.request, urllib.error
import concurrent.futures
from datetime import datetime

ENV_FILE = os.path.expanduser("~/.hermes/.env")
RANK_FILE = "/data/model-probe/model-rank.json"
LOG_FILE = "/data/model-probe/probe.log"

env = {}
with open(ENV_FILE) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")

OR_KEY = env.get('OPENROUTER_API_KEY', '')
MISTRAL_KEY = env.get('MISTRAL_API_KEY', '')
ALI_KEY = env.get('ALIYUN_BAILIAN_API_KEY') or env.get('DASHSCOPE_API_KEY', '')
ALI_URL = 'https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions'
TG_TOKEN = env.get('TELEGRAM_BOT_TOKEN', '')
TG_CHAT = env.get('TELEGRAM_HOME_CHANNEL', '')

# ===== 模型池定义 =====
# local: Ollama 本机（简单任务优先）
LOCAL_MODELS = ["deepseek-r1:1.5b", "qwen3:4b", "phi3.5:3.8b", "deepseek-r1:7b"]
# hard: Ali 百炼（难任务主力）
ALI_MODELS = ["qwen3.8-max"]
# 云端免费池
OR_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    "nex-agi/nex-n2.5-mini:free",
    "poolside/laguna-xs-2.1:free",
    "inclusionai/ling-3.0-flash-fin:free",
    "dots-studio/dots-3-note-preview:free",
    "cohere/north-mini-code:free",
    "deepseek/deepseek-chat:free",
    "deepseek/deepseek-r1:free",
    "meituan/longcat-2.0:free",
    "thinkingmachines/inkling:free",
]
MISTRAL_MODELS = ["ministral-8b-2512", "mistral-small-latest"]

def http_probe(url, headers, body, timeout=25):
    """通用 HTTP 探测，返回 (status, latency_ms, detail)"""
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={**headers, 'Content-Type': 'application/json'})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode())
            latency = int((time.time() - start) * 1000)
            txt = ''
            try:
                txt = (d['choices'][0]['message'].get('content') or '').strip()
            except Exception:
                txt = json.dumps(d)[:60]
            if txt:
                return "ok", latency, ""
            return "reasoning_only", latency, "empty content"
    except urllib.error.HTTPError as e:
        return "dead", int((time.time() - start) * 1000), f"HTTP {e.code}"
    except Exception as e:
        return "dead", int((time.time() - start) * 1000), str(e)[:60]

def probe_local(model):
    # 本地 Ollama：generate 接口，think=false，5 token 快速探测
    try:
        req = urllib.request.Request('http://localhost:11434/api/generate',
            data=json.dumps({"model": model, "prompt": "hi", "stream": False,
                             "think": False, "options": {"num_predict": 5}}).encode(),
            headers={'Content-Type': 'application/json'})
        start = time.time()
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode())
            latency = int((time.time() - start) * 1000)
            if d.get('response'):
                speed = round(d.get('eval_count', 1) / max(d.get('eval_duration', 1) / 1e9, 0.01), 1)
                return "ok", latency, f"{speed} tok/s"
            return "dead", latency, "empty response"
    except Exception as e:
        return "dead", 99999, str(e)[:60]

def probe_one(item):
    kind, model = item
    if kind == 'local':
        st, lat, det = probe_local(model)
        return {"model": model, "provider": "ollama", "tier": "local",
                "status": st, "latency": lat, "detail": det}
    if kind == 'ali':
        st, lat, det = http_probe(ALI_URL, {'Authorization': f'Bearer {ALI_KEY}'},
            {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5})
        return {"model": model, "provider": "alibaba-cn", "tier": "ali",
                "status": st, "latency": lat, "detail": det,
                "base_url": ALI_URL.rsplit('/chat', 1)[0]}
    if kind == 'mistral':
        st, lat, det = http_probe('https://api.mistral.ai/v1/chat/completions',
            {'Authorization': f'Bearer {MISTRAL_KEY}'},
            {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5})
        return {"model": model, "provider": "custom", "tier": "mistral",
                "status": st, "latency": lat, "detail": det}
    if kind == 'or':
        st, lat, det = http_probe('https://openrouter.ai/api/v1/chat/completions',
            {'Authorization': f'Bearer {OR_KEY}'},
            {"model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5})
        return {"model": model, "provider": "openrouter", "tier": "or_free",
                "status": st, "latency": lat, "detail": det}

def tg_alert(text):
    if not TG_TOKEN or not TG_CHAT:
        return
    try:
        req = urllib.request.Request(
            f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data=json.dumps({"chat_id": TG_CHAT, "text": text}).encode(),
            headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass  # 告警失败不阻塞探测

def main():
    os.makedirs(os.path.dirname(RANK_FILE), exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tasks = ([('local', m) for m in LOCAL_MODELS]
             + [('ali', m) for m in ALI_MODELS]
             + [('mistral', m) for m in MISTRAL_MODELS]
             + [('or', m) for m in OR_MODELS])

    print(f"[{now}] 探测 {len(tasks)} 个模型 (local={len(LOCAL_MODELS)}, ali={len(ALI_MODELS)}, mistral={len(MISTRAL_MODELS)}, or={len(OR_MODELS)})")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(probe_one, tasks):
            results.append(r)
            tag = "✅" if r['status'] == 'ok' else ("⚠️" if r['status'] == 'reasoning_only' else "❌")
            print(f"  {tag} [{r['tier']:8}] {r['model']:45} {r['status']:15} {r['latency']}ms {r['detail']}")

    priority = {"ok": 0, "reasoning_only": 1, "dead": 2}
    results.sort(key=lambda x: (priority.get(x['status'], 3), x['latency']))

    ok = lambda tier: [r for r in results if r['tier'] == tier and r['status'] == 'ok']

    # ===== 分层路由策略：简单→本地，难→Ali =====
    simple_pool = ok('local')          # 简单任务 → 本地
    hard_ok = ok('ali')                # 难任务 → Ali
    mid_pool = ok('mistral') + ok('or_free')  # 中间档 → 云端免费

    routing = {
        "simple": {
            "route": [f"ollama/{r['model']}" for r in simple_pool],
            "note": "简单任务(摘要/格式化/短问答)走本地Ollama, 零费用零限流",
        },
        "hard": {
            "route": [{"model": r['model'], "provider": r['provider'],
                       "base_url": r.get('base_url')} for r in hard_ok],
            "note": "难任务(架构/代码/长推理/标书)走Ali百炼 qwen3.8-max",
        },
        "mid_free_cloud": [
            {"model": r['model'], "provider": r['provider'], "tier": r['tier']} for r in mid_pool
        ],
        "fallback_chain_full": (
            ([{"model": r['model'], "provider": "alibaba-cn"} for r in hard_ok]
             + [{"model": r['model'], "provider": r['provider']} for r in mid_pool]
             + [{"model": r['model'], "provider": "ollama"} for r in simple_pool])
        ),
    }

    output = {
        "timestamp": now,
        "summary": {
            "total": len(results),
            "ok": sum(1 for r in results if r['status'] == 'ok'),
            "dead": sum(1 for r in results if r['status'] == 'dead'),
            "local_ok": len(simple_pool),
            "ali_ok": len(hard_ok),
            "free_cloud_ok": len(mid_pool),
        },
        "routing_policy": routing,
        "ranked": results,
    }
    with open(RANK_FILE, 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    with open(LOG_FILE, 'a') as f:
        s = output['summary']
        f.write(f"[{now}] ok={s['ok']}/{s['total']} local={s['local_ok']} ali={s['ali_ok']} freecloud={s['free_cloud_ok']}\n")

    print(f"\n完成: ✅{output['summary']['ok']} ❌{output['summary']['dead']} | "
          f"simple档(本地)={len(simple_pool)} hard档(Ali)={len(hard_ok)} 云端免费={len(mid_pool)}")
    print(f"路由策略已写入 {RANK_FILE}")

    # Ali 主力挂了才告警（本地/免费池挂了不影响主链路）
    if not hard_ok:
        tg_alert(f"⚠️ 模型探测告警 [{now}]\nAli百炼 qwen3.8-max 不可用（难任务主力挂了）！\n当前可用: 本地{len(simple_pool)}个 / 云端免费{len(mid_pool)}个\n详情: /data/model-probe/model-rank.json")

if __name__ == '__main__':
    main()
