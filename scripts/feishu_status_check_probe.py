import json, subprocess, urllib.request, urllib.error, datetime

CRED = json.load(open('/home/ubuntu/.feishu/credentials.json'))
APPID = CRED['app_id']
APPSEC = CRED['app_secret']
CHAT = 'oc_986f621882053506879238b4ab5a81cf'

def post(url, data, headers):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def get(url, headers):
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

# 1) tenant token
tok_resp = post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                {'app_id': APPID, 'app_secret': APPSEC}, {'Content-Type': 'application/json'})
TENANT = tok_resp.get('tenant_access_token')
print('TOKEN code:', tok_resp.get('code'), 'len:', len(TENANT) if TENANT else 0)

H = {'Authorization': f'Bearer {TENANT}', 'Content-Type': 'application/json'}

# 2) bot info
bot = get('https://open.feishu.cn/open-apis/bot/v3/info', H)
print('BOT code:', bot.get('code'))
print('BOT name:', bot.get('bot', {}).get('app_name'))
print('BOT activate_status:', bot.get('bot', {}).get('activate_status'))
print('BOT open_id:', bot.get('bot', {}).get('open_id'))

# 3) attempt send heartbeat
now = datetime.datetime.now().strftime('%H:%M')
send = post('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
            {'receive_id': CHAT, 'msg_type': 'text',
             'content': json.dumps({'text': f'[Feishu 状态自检] Hermes 定时探活 {now} — 若您收到此条，说明机器人已进群且可正常收发。'})},
            H)
print('SEND code:', send.get('code'), 'msg:', send.get('msg'))

# 4) chat info
chat = get(f'https://open.feishu.cn/open-apis/im/v1/chats/{CHAT}', H)
print('CHAT code:', chat.get('code'), 'msg:', chat.get('msg'))
print('CHAT name:', chat.get('data', {}).get('name') if chat.get('code') == 0 else None)
