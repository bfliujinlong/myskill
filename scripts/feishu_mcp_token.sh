#!/bin/bash
# Refresh TAT for feishu MCP
CREDS=/home/ubuntu/.feishu/credentials.json
APP_ID=$(python3 -c "import json; print(json.load(open('$CREDS'))['app_id'])")
APP_SECRET=$(python3 -c "import json; print(json.load(open('$CREDS'))['app_secret'])")
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])"
