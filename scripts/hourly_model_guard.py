#!/usr/bin/env python3
"""
每小时模型守护：同时探测 Nous + OpenRouter 免费模型
策略：取最快的作为主模型，其余作为 fallback，永远保留 nemotron-3.5-lightning 兜底
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── 配置 ─────────────────────────────────────────────────────
ENV_PATH = "/home/ubuntu/.hermes/.env"
CONFIG_PATH = "/home/ubuntu/.hermes/config.yaml"
LOG_PATH = f"/tmp/hourly-model-guard-{time.strftime('%Y%m%d-%H%M%S')}.log"

# ── 候选模型列表 ─────────────────────────────────────────────
NOUS_CANDIDATES = [
    "solar-pro4:free",
    "solar-pro4",
    "solar-mini:free",
    "solar-mini",
    "tencent/hy3:free",
    "tencent/hy3",
    "tencent/hy4-preview:free",
    "tencent/hy4-preview",
    "tencent/hy1.5:free",
    "stepfun/step-3.7-flash",
    "meituan/longcat-2.0",
]

OR_CANDIDATES = [
    "minimax/minimax-m3:free",
    "minimax/minimax-m2.7:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free",
    "google/gemma-4-31b-it:free",
]

ANCHOR = "nvidia/nemotron-3.5-lightning"

# ── 日志 ─────────────────────────────────────────────────────
def log(msg):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")

# ── 读取密钥 ─────────────────────────────────────────────────
def read_keys():
    keys = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    keys["or"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("NOUS_API_KEY="):
                    keys["nous"] = line.split("=", 1)[1].strip().strip('"').strip("'")
    return keys

# ── 探测单个模型 ─────────────────────────────────────────────
def probe_model(provider, model, api_key, base_url, timeout=8):
    """探测一个模型，返回 (provider, model_name, elapsed_ms) 或 None"""
    url = f"{base_url}/chat/completions"
    payload = json.dumps({
        "model": f"{model}:free",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 8
    }).encode()
    
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })
    
    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        elapsed = int((time.time() - start) * 1000)
        if resp.status == 200:
            return (provider, model, elapsed)
    except urllib.error.HTTPError as e:
        pass  # 429/404/403 等都算不可用
    except Exception:
        pass
    return None

# ── 主逻辑 ───────────────────────────────────────────────────
def main():
    log("=== hourly-model-guard start ===")
    
    keys = read_keys()
    log(f"OR_KEY: {'有' if keys.get('or') else '无'} (len={len(keys.get('or', ''))})")
    log(f"NOUS_KEY: {'有' if keys.get('nous') else '无'} (len={len(keys.get('nous', ''))})")
    
    results = []  # (provider, model, elapsed_ms)
    
    # 并发探测
    def probe_wrapper(provider, model, api_key, base_url):
        return probe_model(provider, model, api_key, base_url)
    
    tasks = []
    
    # 添加 Nous 任务
    if keys.get("nous"):
        log(f"开始探测 Nous 端点 ({len(NOUS_CANDIDATES)} 个模型)...")
        for m in NOUS_CANDIDATES:
            tasks.append(("nous", m, keys["nous"], "https://inference-api.nousresearch.com/v1"))
    
    # 添加 OpenRouter 任务
    if keys.get("or"):
        log(f"开始探测 OpenRouter 端点 ({len(OR_CANDIDATES)} 个模型)...")
        for m in OR_CANDIDATES:
            tasks.append(("or", m, keys["or"], "https://openrouter.ai/api/v1"))
    
    if not tasks:
        log("没有可用的 API key，退出")
        return
    
    # 并发执行
    max_workers = min(20, len(tasks))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for provider, model, key, url in tasks:
            future = executor.submit(probe_wrapper, provider, model, key, url)
            futures[future] = (provider, model)
        
        done = 0
        total = len(futures)
        for future in as_completed(futures):
            done += 1
            if done % 10 == 0 or done == total:
                log(f"探测进度: {done}/{total}")
            
            provider, model = futures[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
                    log(f"  ✅ [{provider}] {model} ({result[2]}ms)")
            except Exception as e:
                log(f"  ❌ [{provider}] {model} (异常: {e})")
    
    # 按速度排序
    results.sort(key=lambda x: x[2])
    
    log("")
    log(f"=== 探测结果: 共 {len(results)} 个可用 ===")
    
    nous_ok = [r for r in results if r[0] == "nous"]
    or_ok = [r for r in results if r[0] == "or"]
    
    log(f"Nous 可用: {len(nous_ok)} 个")
    for r in nous_ok:
        log(f"  ✅ {r[1]} ({r[2]}ms)")
    
    log(f"OpenRouter 可用: {len(or_ok)} 个")
    for r in or_ok:
        log(f"  ✅ {r[1]} ({r[2]}ms)")
    
    if not results:
        log("❌ 没有任何模型可用，保留现有配置")
        return
    
    # 构建 fallback 列表（不含 anchor）
    fallback = []
    anchor_in_results = False
    for r in results:
        if r[1] == ANCHOR:
            anchor_in_results = True
        else:
            fallback.append(r)
    
    # 如果 anchor 不在结果中，把它加进去作为兜底
    if not anchor_in_results:
        log(f"⚠️  Anchor '{ANCHOR}' 不在可用列表中，将不添加兜底")
    
    # 主模型 = 最快的
    primary = fallback[0]
    primary_provider = primary[0]
    primary_model = primary[1]
    
    # 确定最终 provider/base_url
    if primary_provider == "nous":
        final_provider = "nous"
        final_base_url = "https://inference-api.nousresearch.com/v1"
    else:
        final_provider = "openrouter"
        final_base_url = "https://openrouter.ai/api/v1"
    
    log("")
    log(f"主模型 → {primary_model} ({primary_provider})")
    if anchor_in_results:
        log(f"兜底模型 → {ANCHOR}:free")
    
    # 写 config.yaml
    fb_models = [(r[0], r[1]) for r in fallback]
    
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f) or {}
    
    config.setdefault("model", {})
    config["model"]["default"] = f"{primary_model}:free"
    config["model"]["provider"] = final_provider
    config["model"]["base_url"] = final_base_url
    config["model"]["fallback_providers"] = [
        {"provider": fp, "model": f"{fm}:free"} for fp, fm in fb_models
    ]
    
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True, width=120)
    
    log("")
    log("=== 写 config.yaml 完成 ===")
    log(f"  default: {primary_model}:free")
    log(f"  provider: {final_provider}")
    log(f"  base_url: {final_base_url}")
    log(f"  fallback_providers: {len(fb_models)} 个")
    for fp, fm in fb_models:
        log(f"    - {fp}/{fm}:free")
    
    log("")
    log(f"=== 完成 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===")
    log(f"日志: {LOG_PATH}")

if __name__ == "__main__":
    main()
