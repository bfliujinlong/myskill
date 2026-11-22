#!/usr/bin/env bash
set -euo pipefail
CRED="/home/ubuntu/.feishu/credentials.json"
CHAT_ID="oc_986f621882053506879238b4ab5a81cf"
APP_ID=$(python3 -c "import json;print(json.load(open('$CRED'))['app_id'])")
APP_SEC=$(python3 -c "import json;print(json.load(open('$CRED'))['app_secret'])")

echo "APP_ID: $APP_ID"

# 1) tenant_access_token
TOK_RESP=$(curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SEC\"}")
echo "TOKEN_API: $(echo "$TOK_RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print('code=',d.get('code'),'msg=',d.get('msg'))")"
TOK=$(echo "$TOK_RESP" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tenant_access_token',''))")
if [ -z "$TOK" ]; then
  echo "RESULT: CANNOT_OBTAIN_TOKEN (app disabled / secret wrong / not published)"
  exit 0
fi
echo "TOKEN_OK: yes"

H_AUTH="Authorization: Bearer $TOK"

# 2) bot info
BOT_RESP=$(curl -s "https://open.feishu.cn/open-apis/bot/v3/info" -H "$H_AUTH")
echo "BOT_INFO: $(echo "$BOT_RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print('code=',d.get('code'),'app_name=',d.get('bot',{}).get('app_name'),'activate_status=',d.get('bot',{}).get('activate_status'))")"

# 3) list chats bot is member of
LIST_RESP=$(curl -s "https://open.feishu.cn/open-apis/im/v1/chats?page_size=50&user_id_type=open_id" -H "$H_AUTH")
echo "CHAT_LIST: $(echo "$LIST_RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print('code=',d.get('code'),'count=',len(d.get('data',{}).get('items',[])))")"
IN_LIST=$(echo "$LIST_RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);items=d.get('data',{}).get('items',[]);print('yes' if any(i.get('chat_id')=='$CHAT_ID' for i in items) else 'no')")
echo "TARGET_IN_MEMBER_LIST: $IN_LIST"

# 4) direct chat info fetch
CHAT_RESP=$(curl -s "https://open.feishu.cn/open-apis/im/v1/chats/$CHAT_ID?user_id_type=open_id" -H "$H_AUTH")
echo "CHAT_INFO: $(echo "$CHAT_RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print('code=',d.get('code'),'msg=',d.get('msg'))")"
