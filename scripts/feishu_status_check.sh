#!/usr/bin/env bash
# Feishu workspace status check — token + bot info + home-channel send probe
set -o pipefail

APPID=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.feishu/credentials.json'))['app_id'])")
APPSEC=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.feishu/credentials.json'))['app_secret'])")

# 1. tenant_access_token
TOK=$(curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APPID\",\"app_secret\":\"$APPSEC\"}" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('tenant_access_token',''))")
if [ -z "$TOK" ]; then
  echo "TOKEN_EXCHANGE_FAILED"
  exit 1
fi
echo "TOKEN_OK len=${#TOK}"

# 2. bot info
curl -s https://open.feishu.cn/open-apis/bot/v3/info \
  -H "Authorization: Bearer $TOK" | python3 -m json.tool
echo "---"

# 3. send probe to home channel
CH="oc_986f621882053506879238b4ab5a81cf"
curl -s "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$CH\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\\":\\\"[Feishu 状态自检] 探测消息，请忽略。\\\"}\"}" \
  | python3 -m json.tool
