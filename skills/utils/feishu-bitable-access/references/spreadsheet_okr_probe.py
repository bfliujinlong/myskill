#!/usr/bin/env python3
"""
飞书 anchnet OKR 周报(电子表格 spreadsheet)对比+补列 探针。
实测: OKR 周报 wiki 是 ELECTRONIC SPREADSHEET (obj_type=sheet), 不是多维表格,
所以必须用 sheets/v2 API, 不能套 bitable/v1。主应用 cli_aa093013dc38dcbb 即可读。

用法: python3 spreadsheet_okr_probe.py
会输出:
  1) 两个 wiki 节点的 obj_type 与 spreadsheet token
  2) 本周表 D7dkp8 全部行的 SEQ(B列)/进度(O列)/TASK(E列)
  3) 与上周对比, 找出本周新达成 100% 的行 (供补 G/H 列)

依赖: 无第三方库, 仅标准库 urllib。
凭证: /home/ubuntu/.feishu/credentials.json (主应用)
"""
import json, urllib.request, urllib.error

CRED = "/home/ubuntu/.feishu/credentials.json"
cred = json.load(open(CRED))
APPID, APPSEC = cred["app_id"], cred["app_secret"]

def call(url, method="GET", data=None, token=None, q=None):
    if q: url = f"{url}?{q}"
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        try: j = json.loads(e.read().decode())
        except Exception: j = {"msg": e.read().decode()[:300]}
        return None, {"http": e.code, **j}
    except Exception as e:
        return None, {"http": "EXC", "msg": str(e)}

# 1) tenant token
r, _ = call("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            method="POST", data=json.dumps({"app_id": APPID, "app_secret": APPSEC}).encode())
token = r["tenant_access_token"]

# 2) wiki 节点 -> 判定 obj_type + spreadsheet token
WEEKS = {
    "last": "U8sEw05S6iO9fwk48r6cCm91n4c",
    "this": "F3Y6w2PGOiyc1MkMpDlcBcnQnrh",
}
TAB = "D7dkp8"
tokens = {}
for label, wiki in WEEKS.items():
    n, e = call("https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node",
                method="GET", token=token, q=f"token={wiki}&obj_type=wiki")
    nd = n["data"]["node"]
    print(f"[{label}] obj_type={nd.get('obj_type')}  spreadsheet_token={nd.get('obj_token')}")
    tokens[label] = nd.get("obj_token")

# 3) 读本周整表
SP = tokens["this"]
d, e = call(f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SP}/values/{TAB}!A1:Z400",
            token=token, q="valueRenderOption=ToString")
vals = d["data"]["valueRange"]["values"]
header = vals[0]
print("HEADER:", header)

# 4) 定位 SEQ->行号, 打印 进度/备注
last_vals = call(f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{tokens['last']}/values/{TAB}!A1:Z400",
                 token=token, q="valueRenderOption=ToString")[0]["data"]["valueRange"]["values"]
def pct(v):
    try: return float(v)
    except: return None
last_prog = {row[1]: pct(row[14]) for row in last_vals[1:] if len(row) > 14 and row[1]}
print("\n=== 本周各个 OKR 进度 & 较上周变化 ===")
for i, row in enumerate(vals[1:]):
    if len(row) > 1 and row[1]:
        seq = row[1]
        p = pct(row[14]) if len(row) > 14 else None
        lp = last_prog.get(seq)
        flag = ""
        if p == 1.0 and (lp is None or lp < 1.0):
            flag = "  <== 本周新达成 100%"
        print(f"  {seq} (row {i+2}): 进度={p} 上周={lp}{flag}")

# 5) 写回示例 (补 G/H 列; 需 sheets:spreadsheet 读写权限, 否则 403)
# body = {"valueRange": {"range": f"{TAB}!G{row}:H{row}",
#                        "values": [[g_text, h_text]]}}
# call(f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SP}/values",
#      method="PUT", data=json.dumps(body).encode(), token=token)
print("\n[写回] 取消注释第5段 + 用户开 sheets:spreadsheet 读写权限并发布版本后即可写入 G/H 列。")
