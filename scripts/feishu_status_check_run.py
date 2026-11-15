import json, urllib.request, urllib.error

CRED = "/home/ubuntu/.feishu/credentials.json"
with open(CRED) as f:
    c = json.load(f)
APPID, APPSEC = c["app_id"], c["app_secret"]

def post(url, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, {"error": str(e.reason)}

def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except:
            return e.code, {"error": str(e.reason)}

print("=== tenant_access_token ===")
st, body = post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
                {"app_id": APPID, "app_secret": APPSEC})
print("status:", st, "code:", body.get("code"), "msg:", body.get("msg"))
TOK = body.get("tenant_access_token")
print("token_len:", len(TOK) if TOK else 0)

if not TOK:
    print("FATAL: cannot get token, aborting")
else:
    print("\n=== app info ===")
    st, body = get(f"https://open.feishu.cn/open-apis/application/v6/applications/{APPID}?lang=zh-CN", TOK)
    print("status:", st, "code:", body.get("code"), "msg:", body.get("msg"))
    if "data" in body:
        d = body["data"]
        print("app_name:", d.get("app_name"))
        print("status:", d.get("status"), "(1=已上线/启用, 0=停用)")
        print("online_status:", d.get("online_status"))
        print("is_appstore_app:", d.get("is_appstore_app"))

    CHAT = "oc_986f621882053506879238b4ab5a81cf"
    print("\n=== bot membership in chat ===")
    st, body = get(f"https://open.feishu.cn/open-apis/im/v1/chats/{CHAT}/members/me", TOK)
    print("status:", st, "code:", body.get("code"), "msg:", body.get("msg"))
    print(json.dumps(body, ensure_ascii=False)[:400])

    print("\n=== test send message to chat ===")
    st, body = post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
                    {"receive_id": CHAT, "msg_type": "text", "content": json.dumps({"text": "[cron] Feishu status check probe - bot reachable"})},
                    TOK)
    print("status:", st, "code:", body.get("code"), "msg:", body.get("msg"))
    print(json.dumps(body, ensure_ascii=False)[:400])
