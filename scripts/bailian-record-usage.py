#!/usr/bin/env python3
"""百炼 Token 用量记录器 - 每次 API 调用后记录 token 消耗到本地账本
用法: python3 bailian-record-usage.py <prompt_tokens> <completion_tokens> [model]
"""
import json, sys, os
from datetime import datetime

LEDGER = os.path.expanduser("~/.hermes/scripts/bailian_usage_ledger.json")

# 百炼按量计费 (元/百万tokens)
PRICING = {
    "glm-5.2": {"input": 8, "output": 28},
    "qwen3.8-max": {"input": 12, "output": 36},
    "qwen3.7-max": {"input": 10, "output": 30},
}

# Token Plan: Lite 39元/月, 2500 credits/7天
# 单 credit ≈ 39 / (2500 * 4周) ≈ 0.0039元
CREDIT_PRICE = 0.0039

def record(prompt_tokens, completion_tokens, model="glm-5.2"):
    pricing = PRICING.get(model, PRICING["glm-5.2"])
    cost = (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1_000_000
    credits = cost / CREDIT_PRICE
    
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_cny": round(cost, 6),
        "credits": round(credits, 4)
    }
    
    data = {"entries": []}
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            try:
                data = json.load(f)
            except:
                data = {"entries": []}
    
    data["entries"].append(entry)
    
    with open(LEDGER, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return entry

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 bailian-record-usage.py <prompt_tokens> <completion_tokens> [model]")
        sys.exit(1)
    
    pt = int(sys.argv[1])
    ct = int(sys.argv[2])
    model = sys.argv[3] if len(sys.argv) > 3 else "glm-5.2"
    
    e = record(pt, ct, model)
    print(f"已记录: {e['prompt_tokens']}+{e['completion_tokens']} tokens, {e['credits']} credits, ¥{e['cost_cny']}")
