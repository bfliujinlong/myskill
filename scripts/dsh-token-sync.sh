#!/usr/bin/env bash
# 同步 Hermes 的 Nous OAuth access_token 到 dsh 的 credentials 文件
# Hermes 的 token 约 1 小时过期，由 Hermes 自动续期；本脚本每分钟把最新 token 注入 dsh
set -euo pipefail

NOUS_AUTH="/home/ubuntu/.hermes/shared/nous_auth.json"
CRED_FILE="/home/ubuntu/.dsh/.credentials.yaml"

if [[ ! -f "$NOUS_AUTH" ]]; then
  echo "$(date) [skip] nous_auth.json 不存在"
  exit 0
fi

TOKEN=$(python3 -c "import json,sys; print(json.load(open('$NOUS_AUTH')).get('access_token',''))" 2>/dev/null || true)
if [[ -z "$TOKEN" ]]; then
  echo "$(date) [skip] 无法读取 access_token"
  exit 0
fi

# 写入 credentials 文件 (保留其他字段，仅更新两个 key)
python3 - "$CRED_FILE" "$TOKEN" <<'PY'
import sys, re
path, token = sys.argv[1], sys.argv[2]
content = ""
try:
    with open(path) as f:
        content = f.read()
except FileNotFoundError:
    pass
# 替换或追加 DEEPSEEK_API_KEY / NOUS_API_KEY
updated = False
def repl(m):
    global updated
    updated = True
    return f"{m.group(1)}: {token}"
content = re.sub(r'^(DEEPSEEK_API_KEY):\s*.*$', lambda m: f"DEEPSEEK_API_KEY: {token}", content, flags=re.M)
content = re.sub(r'^(NOUS_API_KEY):\s*.*$', lambda m: f"NOUS_API_KEY: {token}", content, flags=re.M)
if 'DEEPSEEK_API_KEY:' not in content:
    content += f"\nDEEPSEEK_API_KEY: {token}\n"
if 'NOUS_API_KEY:' not in content:
    content += f"NOUS_API_KEY: {token}\n"
with open(path, 'w') as f:
    f.write(content)
print("synced")
PY

chmod 600 "$CRED_FILE" 2>/dev/null || true
echo "$(date) [ok] token 已同步到 $CRED_FILE"
