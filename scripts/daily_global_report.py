#!/usr/bin/env python3
"""
daily_global_report.py — 全局巡检报告 v3（丰富版）
每项检查带阈值分级（✅绿/⚠️黄/🔴红）+ 趋势对比 + 异常标注
"""
import subprocess, json, time, os, sys
from datetime import datetime, date
from collections import defaultdict

# ─── 颜色常量 ───────────────────────────────────────────────
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
C = "\033[96m"; W = "\033[97m"; BOLD = "\033[1m"; RESET = "\033[0m"
RED_BG  = "\033[41m"; YEL_BG = "\033[43m"

def col(tag, cond="green"):
    m = {"red":R,"green":G,"yellow":Y,"blue":B,"cyan":C,"white":W}
    return f"{m.get(cond,R)}{tag}{RESET}"

def warn(tag): return col(f"⚠ {tag}", "yellow")
def fail(tag): return col(f"🔴 {tag}", "red")
def ok(tag):   return col(f"✅ {tag}", "green")
def info(tag): return col(f"ℹ {tag}", "cyan")

NOW  = datetime.now().astimezone()
TS   = NOW.strftime("%Y-%m-%d %H:%M %Z")
DATE = NOW.strftime("%Y-%m-%d")

VENV     = "/home/ubuntu/oci-monitor/venv"
OCI_BIN  = f"{VENV}/bin/oci"
PY       = f"{VENV}/bin/python3"
os.environ["OCI_CONFIG_DIR"] = "/home/ubuntu/.oci"
TENANT   = "ocid1.tenancy.oc1..aaaaaaaax6j4qdqjvsmgkouo3xvzuvvg7w4wgca33q5y2sap5773n6mdgdgq"
REGION   = "eu-frankfurt-1"

HISTORY_FILE = "/tmp/.report_history.json"

def run(cmd, timeout=15, decode=True):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if decode else r.stdout
    except Exception as e:
        return f"[ERROR] {e}"

def curl_code(url, timeout=5):
    r = subprocess.run(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time {timeout} {url}",
                       shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def pct_used(path="/"):
    r = run(f"df -h {path} | tail -1 | awk '{{print $5}}'")
    return int(r.replace("%","")) if r.isdigit() else 0

def mem_pct():
    r = run("free | grep Mem | awk '{printf \"%.0f\", $3/$2*100}'")
    return int(r) if r.isdigit() else 0

def load():
    r = run("cat /proc/loadavg | awk '{print $1,$2,$3}'")
    return r or "N/A"

def cpu_count():
    r = run("nproc")
    return int(r) if r.isdigit() else 1

def is_active(service):
    r = run(f"systemctl is-active {service}")
    return r == "active"

def pgrep(pat):
    r = run(f"pgrep -f '{pat}' 2>/dev/null")
    if not r or "No such" in r or r.strip() == "": return False
    pids = [l.strip() for l in r.splitlines() if l.strip().isdigit()]
    return len(pids) > 0

# ─── 读取历史（用于趋势对比）────────────────────────────────
def read_history():
    try:
        return json.load(open(HISTORY_FILE))
    except:
        return {}

def write_history(data):
    try:
        json.dump(data, open(HISTORY_FILE,"w"))
    except: pass

# ─── 分隔线 ────────────────────────────────────────────────
DIV = f"{B}{'─'*62}{RESET}"
BIG = f"{B}{BOLD}{'═'*62}{RESET}"

def section(title):
    print(f"\n{BIG}")
    print(f"{B}{BOLD}  {title}{RESET}")
    print(BIG)

def kv(key, val, cond="green"):
    icon = {"green":"✅","yellow":"⚠️","red":"🔴","cyan":"ℹ️"}.get(cond,"")
    print(f"  {icon} {key:<36} {val}")

# ═══════════════════════════════════════════════════════════════
# 1. OCI 费用（阈值：>$0.05 = 告警）
# ═══════════════════════════════════════════════════════════════
def check_oci_cost(hist):
    section("一、OCI 费用明细")
    start = datetime.utcnow().replace(day=1).strftime("%Y-%m-%d")
    end   = (datetime.utcnow().date().strftime("%Y-%m-%d"))

    raw = run(f'{OCI_BIN} usage-api usage-summary request-summarized-usages '
              f'--region {REGION} --tenant-id {TENANT} '
              f'--time-usage-started {start} --time-usage-ended {end} '
              f'--granularity DAILY 2>/dev/null')

    try:
        d = json.loads(raw) if raw else {}
        items = d.get("data",{}).get("items",[])
    except:
        items = []

    total = 0.0
    by_day = {}
    for it in items:
        amt = float(it.get("computed-amount") or it.get("cost") or 0)
        day = it.get("time-usage-started","")[:10]
        by_day[day] = by_day.get(day,0) + amt
        total += amt

    cur = items[0].get("currency","SGD") if items else "SGD"
    cny = total * 5.3
    active_days = len([v for v in by_day.values() if v > 0])

    # 阈值判断
    if total <= 0.001:
        kv("当月总费用", f"${total:.4f} {cur} ≈ ¥{cny:.2f}  → {ok('免费额度内，零消费')}")
    elif total <= 0.05:
        kv("当月总费用", f"${total:.4f} {cur} ≈ ¥{cny:.2f}  → {warn('恒定遗账，免费额度内')}")
    else:
        kv("当月总费用", f"${total:.4f} {cur} ≈ ¥{cny:.2f}  → {fail('有新增消费，请核查')}")

    kv("活跃计费日", f"{active_days} 天")
    kv("日均", f"${total/max(active_days,1):.4f}" if active_days else "N/A")

    if by_day:
        print(f"  {DIV}")
        for day, amt in sorted(by_day.items()):
            flag = "🔴" if amt > 0.05 else ("⚠️" if amt > 0.001 else "✅")
            print(f"    {flag} {day}  ${amt:.4f}")

    # 趋势
    prev = hist.get("oci_cost", 0)
    delta = total - prev
    if delta > 0.01:
        kv("较昨日", f"↑ ${delta:.4f} {fail('上升')}")
    elif delta < -0.001:
        kv("较昨日", f"↓ ${abs(delta):.4f} {ok('下降')}")
    else:
        kv("较昨日", "→ 持平")

    return total

# ═══════════════════════════════════════════════════════════════
# 2. 系统资源（阈值：CPU>4、内存>85%、磁盘>85%、inode>85%）
# ═══════════════════════════════════════════════════════════════
def check_resources(hist):
    section("二、系统资源")

    # CPU
    load_val = load()
    ncpu = cpu_count()
    load1 = float(load_val.split()[0]) if load_val != "N/A" else 0
    cpu_cond = "red" if load1 > ncpu*2 else ("yellow" if load1 > ncpu else "green")
    kv("CPU 负载", f"{load_val}  ({ncpu}核)", cpu_cond)
    kv("CPU 使用率", f"{load1/ncpu*100:.1f}%" if ncpu else "N/A",
       "red" if load1/ncpu > 100 else "green")

    # 内存
    mem = mem_pct()
    mem_cond = "red" if mem > 85 else ("yellow" if mem > 75 else "green")
    kv("内存使用率", f"{mem}%", mem_cond)

    # 磁盘
    disk = pct_used("/")
    disk_cond = "red" if disk > 90 else ("yellow" if disk > 80 else "green")
    kv("根分区使用率", f"{disk}%", disk_cond)

    # 数据盘（检查 /dev/sdb 是否挂载到 /data）
    disk_data = 0
    df_data = run("df -h /data 2>/dev/null | tail -1")
    if df_data and ("/dev/sdb" in df_data or "sdb" in df_data.split()[0]):
        disk_data = int(df_data.split()[4].replace("%","")) if len(df_data.split()) >= 5 else 0
    disk_d_cond = "red" if disk_data > 90 else ("yellow" if disk_data > 85 else "green")
    kv("数据盘 /data", f"{disk_data}%", disk_d_cond)

    # inodes
    inode = run("df -i / | tail -1 | awk '{print $5}'")
    inode_pct = int(inode.replace("%","")) if inode.replace("%","").isdigit() else 0
    inode_cond = "red" if inode_pct > 90 else ("yellow" if inode_pct > 80 else "green")
    kv("inode 使用率", f"{inode_pct}%", inode_cond)

    # 磁盘 IO
    io = run("iostat -x 1 2 2>/dev/null | grep '^%' || cat /proc/diskstats | head -3")
    kv("磁盘 IO", io[:80] if io else "N/A")

    # 趋势对比
    prev_mem = hist.get("mem_pct", mem)
    kv("内存趋势", f"昨日 {prev_mem}% → 今日 {mem}%  "
       + (fail("↑") if mem > prev_mem else (ok("↓") if mem < prev_mem else "→")))

    return {"mem":mem,"disk":disk,"inode":inode_pct}

# ═══════════════════════════════════════════════════════════════
# 3. 运行服务（逐个检查）
# ═══════════════════════════════════════════════════════════════
SERVICES = [
    ("nginx",           "nginx"),
    ("cloudflared",     "cloudflared"),
    ("cloudflared-dsh", "cloudflared-dsh"),
    ("litellm-gateway", "litellm"),
    ("codex-filter",    "python3.*4101"),
    ("hermes-gateway",  "hermes-gateway"),
    ("dsh",             "dsh"),
    ("cron",            "cron"),
    ("rsyslog",         "rsyslog"),
    ("sshd",            "sshd"),
    ("crowdsec",        "crowdsec"),
]

def check_services():
    section("三、运行服务")
    all_ok = True
    for name, pat in SERVICES:
        alive = pgrep(pat)
        if alive is None:
            alive = is_active(name) if os.path.exists("/etc/systemd/system") else pgrep(pat)
        status = ok("运行中") if alive else fail("已停止")
        if not alive: all_ok = False
        kv(name, status, "green" if alive else "red")

    # 端口检测
    print(f"\n  {DIV}")
    ports = [
        ("nginx 3080",    "http://127.0.0.1:3080/",           3),
        ("litellm 4100",  "http://127.0.0.1:4100/health",     3),
        ("codex 4101",    "http://127.0.0.1:4101/health",     3),
        ("dsh 3081",      "http://127.0.0.1:3081/health",     3),
        ("tg-relay 8099",  "http://127.0.0.1:8099/docs",      3),
    ]
    for label, url, to in ports:
        code = curl_code(url, to)
        cond = "green" if code == "200" else ("yellow" if code in ("000","403") else "red")
        kv(label, f"HTTP {code}", cond)

    return all_ok

# ═══════════════════════════════════════════════════════════════
# 4. 网络连接
# ═══════════════════════════════════════════════════════════════
def check_network():
    section("四、网络连接")

    # 公网 IP
    pub_ip = run("curl -s --max-time 5 https://ifconfig.me")
    kv("公网 IP", pub_ip if pub_ip else fail("获取失败"))

    # Cloudflare 隧道
    cf_ok = is_active("cloudflared.service")
    cf2_ok = is_active("cloudflared-dsh.service")
    kv("Cloudflare 隧道(主)", "✅ 活跃" if cf_ok else fail("已停止"), "green" if cf_ok else "red")
    kv("Cloudflare 隧道(dsh)", "✅ 活跃" if cf2_ok else warn("已停止"), "green" if cf2_ok else "yellow")

    # DNS 解析
    dns_ok = run("host api.dingtalk.com 2>/dev/null | head -1")
    kv("钉钉 API DNS", dns_ok[:60] if dns_ok else fail("解析失败"), "green" if dns_ok else "red")

    # 连通性（多目标）
    targets = [
        ("google.com",   "https://www.google.com"),
        ("cloudflare",   "https://www.cloudflare.com"),
        ("OCI API",      "https://objectstorage.eu-frankfurt-1.oraclecloud.com"),
        ("OCI 法兰克福", "https://iaas.eu-frankfurt-1.oraclecloud.com"),
        ("ifconfig.me",  "https://ifconfig.me"),
    ]
    print(f"\n  {DIV}")
    for name, url in targets:
        code = curl_code(url, 5)
        cond = "green" if code == "200" else ("yellow" if code in ("000","403","301") else "red")
        kv(name, f"HTTP {code}", cond)

# ═══════════════════════════════════════════════════════════════
# 5. 定时任务
# ═══════════════════════════════════════════════════════════════
def check_cron():
    section("五、定时任务 (Hermes Cron)")
    out = run("hermes cron list 2>/dev/null | head -30")
    if out:
        lines = out.split("\n")
        print(f"  共 {len([l for l in lines if l.strip()])} 个任务")
        for l in lines[:20]:
            if l.strip():
                print(f"  {l}")
    else:
        kv("Hermes Cron", fail("列表为空或调用失败"))

    # 系统 crontab
    out2 = run("crontab -l 2>/dev/null | head -10")
    if out2:
        print(f"\n  {DIV}")
        print(f"  系统 Crontab ({len(out2.splitlines())} 条):")
        for l in out2.splitlines()[:8]:
            print(f"    {l}")

# ═══════════════════════════════════════════════════════════════
# 6. GitHub 备份
# ═══════════════════════════════════════════════════════════════
def check_backup():
    section("六、备份状态 (GitHub)")
    git_dir = "/home/ubuntu/.hermes"
    if not os.path.exists(f"{git_dir}/.git"):
        kv("Git 仓库", fail("未初始化"))
        return

    last = run(f"git -C {git_dir} log -1 --format='%h %s | %cr' 2>/dev/null")
    untracked = run(f"git -C {git_dir} status --porcelain | wc -l 2>/dev/null")
    ahead = run(f"git -C {git_dir} rev-list HEAD..origin/master --count 2>/dev/null")

    kv("最后提交", last if last else warn("无提交"))
    kv("未跟踪文件", untracked if untracked else "0", "yellow" if int(untracked or 0) > 10 else "green")
    kv("待推送提交", ahead if ahead else "0", "yellow" if int(ahead or 0) > 0 else "green")

    # 备份脚本是否存在
    backup_script = "/home/ubuntu/oci-monitor/sync_github.sh"
    if os.path.exists(backup_script):
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_script)).strftime("%Y-%m-%d %H:%M")
        kv("同步脚本", f"存在 ({mtime})")
    else:
        kv("同步脚本", warn("不存在"))

# ═══════════════════════════════════════════════════════════════
# 7. 安全状态
# ═══════════════════════════════════════════════════════════════
def check_security():
    section("七、安全状态")

    # CrowdSec
    if os.path.exists("/usr/bin/crowdsec"):
        cs_ok = is_active("crowdsec")
        kv("CrowdSec", "✅ 运行中" if cs_ok else fail("已停止"), "green" if cs_ok else "red")
        bans = run("cscli decisions list -o json 2>/dev/null | python3 -c "
                   "'import sys,json;d=json.load(sys.stdin);print(len(d))' 2>/dev/null || echo 0")
        ban_cond = "red" if int(bans or 0) > 50 else ("yellow" if int(bans or 0) > 10 else "green")
        kv("已封禁 IP 数", bans, ban_cond)

        # 最近 ban 记录
        recent = run("cscli decisions list --recent 2 2>/dev/null | tail -3")
        if recent:
            print(f"    最近封禁: {recent[:100]}")
    else:
        kv("CrowdSec", info("未安装"))

    # SSH 暴力破解
    today = DATE
    failed = run(f"grep -c 'Failed password' /var/log/auth.log 2>/dev/null | head -1 || echo 0")
    accepted = run(f"grep -c 'Accepted' /var/log/auth.log 2>/dev/null | head -1 || echo 0")
    fi = int(failed or 0)
    ai = int(accepted or 0)
    ssh_cond = "red" if fi > 100 else ("yellow" if fi > 20 else "green")
    kv("SSH 失败登录(今日)", f"{fi} 次", ssh_cond)
    kv("SSH 成功登录(今日)", f"{ai} 次", "green" if ai > 0 else "yellow")

    # 异常 IP
    bad_ips = run("grep 'Failed password' /var/log/auth.log 2>/dev/null | "
                  "awk '{print $11}' | sort | uniq -c | sort -rn | head -5")
    if bad_ips and int(bad_ips.split()[0]) > 10:
        print(f"\n  {warn('Top 攻击源 IP:')}")
        for line in bad_ips.splitlines()[:5]:
            print(f"    {line}")

    # fail2ban
    f2b = run("fail2ban-client status 2>/dev/null | head -5")
    kv("fail2ban", f2b if f2b else info("未安装"), "green" if f2b else "cyan")

# ═══════════════════════════════════════════════════════════════
# 8. 模型健康检查
# ═══════════════════════════════════════════════════════════════
def check_models():
    section("八、模型健康")

    # Hermes 当前配置
    default_model = run("hermes config get model.default 2>/dev/null || echo N/A")
    defaultProv   = run("hermes config get model.provider 2>/dev/null || echo N/A")
    kv("当前默认模型", default_model)
    kv("Provider", defaultProv)

    # 免费模型可用性
    print(f"\n  {DIV}")
    models = [
        ("nous/Hy3",         "https://inference-api.nousresearch.com/v1/models",              8),
        ("OpenRouter",       "https://openrouter.ai/api/v1/models",                            8),
        ("OpenRouter 推理",  "https://openrouter.ai/api/v1/models?extended_thinking=0",       8),
    ]
    results = []
    for name, url, to in models:
        code = curl_code(url, to)
        latency = None
        if code in ("200","301","302"):
            t0 = time.time()
            subprocess.run(f"curl -s -o /dev/null --max-time {to} {url}", shell=True)
            latency = (time.time() - t0) * 1000
            results.append((name, "200", latency))
            kv(name, f"✅ 可用  ({latency:.0f}ms)", "green")
        else:
            results.append((name, code, None))
            kv(name, f"❌ HTTP {code}", "red")

    # Azure
    azure_key = os.environ.get("AZURE_OPENAI_KEY","")
    if azure_key and len(azure_key) > 10:
        kv("Azure OpenAI", info("已配置 key（隐藏）"))
    else:
        kv("Azure OpenAI", warn("未配置"))

    return results

# ═══════════════════════════════════════════════════════════════
# 9. Azure OpenAI 花费
# ═══════════════════════════════════════════════════════════════
def check_azure():
    section("九、Azure OpenAI (gpt-5-mini)")
    ledger_file = os.path.expanduser("~/.hermes/logs/azure_spend_ledger.json")
    if os.path.exists(ledger_file):
        try:
            d = json.load(open(ledger_file))
            total = d.get("total_cost", 0)
            tokens = d.get("total_tokens", 0)
            calls  = d.get("total_calls", 0)
            thresh = 50.0
            pct = total / thresh * 100
            cond = "red" if total > thresh else ("yellow" if total > thresh*0.7 else "green")
            kv("累计费用", f"${total:.4f} / ${thresh} ({pct:.1f}%)", cond)
            kv("调用次数", str(calls))
            kv("Token总量", f"{tokens:,}")
            if total > thresh:
                kv("告警", fail(f"超过阈值 ${thresh}！"))
            else:
                kv("状态", ok(f"安全，剩余 ${thresh-total:.2f}"))
        except Exception as e:
            kv("账本", warn(f"解析失败: {e}"))
    else:
        kv("本地账本", warn("不存在"))

# ═══════════════════════════════════════════════════════════════
# 10. MCP 服务器
# ═══════════════════════════════════════════════════════════════
def check_mcp():
    section("十、MCP 服务器")
    out = run("hermes mcp list 2>/dev/null")
    if out:
        lines = [l for l in out.splitlines() if l.strip()]
        print(f"  共 {len(lines)} 个 MCP 工具")
        for l in lines[:15]:
            print(f"    {l}")
    else:
        kv("MCP", info("无配置或调用失败"))

# ═══════════════════════════════════════════════════════════════
# 11. 系统更新
# ═══════════════════════════════════════════════════════════════
def check_updates():
    section("十一、系统更新")
    upd = run("apt list --upgradable 2>/dev/null | grep -c 'upgradable' 2>/dev/null | tail -1 || echo 0")
    up_cnt = int(upd.strip() or 0)
    upd_cond = "red" if up_cnt > 20 else ("yellow" if up_cnt > 5 else "green")
    kv("可更新包", f"{up_cnt} 个", upd_cond)

    if up_cnt > 0:
        detail = run("apt list --upgradable 2>/dev/null | grep upgradable | head -8")
        if detail:
            print(f"\n  {warn('待更新 (前8):')}")
            for l in detail.splitlines()[:8]:
                print(f"    {l}")

    # 内核
    kv("内核版本", run("uname -r"))
    kv("安全补丁", run("cat /proc/version | head -1")[:60] if run("cat /proc/version") else "N/A")

# ═══════════════════════════════════════════════════════════════
# 12. 日志异常检测（最近 1 小时 ERROR/WARN）
# ═══════════════════════════════════════════════════════════════
def check_logs():
    section("十二、日志异常 (最近 1 小时)")

    # Hermes gateway 日志
    log_file = "/home/ubuntu/.hermes/logs/gateway.log"
    errors = []
    if os.path.exists(log_file):
        # 最近 1 小时的行
        cutoff = int(time.time()) - 3600
        for line in open(log_file):
            try:
                ts_str = line[:19]
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                if dt.timestamp() > cutoff and any(k in line.upper() for k in ["ERROR","EXCEPTION","TRACE","CRITICAL"]):
                    errors.append(line.strip()[:120])
            except:
                pass

    if errors:
        print(f"  {fail(f'发现 {len(errors)} 条异常:')}")
        seen = set()
        for e in errors[-10:]:
            short = e[-80:]
            if short not in seen:
                print(f"    {short}")
                seen.add(short)
    else:
        kv("Gateway 日志", ok("近1小时无 ERROR/CRITICAL"))

    # journald 最近错误
    jerr = run("journalctl --since '1 hour ago' -p err --no-pager -n 5 2>/dev/null | grep -v '^--' | tail -5")
    if jerr:
        print(f"\n  {warn('journald 错误:')}")
        for l in jerr.splitlines():
            if l.strip():
                print(f"    {l[:100]}")

# ═══════════════════════════════════════════════════════════════
# 13. Hermes Gateway 自身状态
# ═══════════════════════════════════════════════════════════════
def check_hermes():
    section("十三、Hermes Gateway 状态")

    pid = run("pgrep -f 'hermes-gateway' | head -1")
    kv("Gateway PID", pid if pid else fail("未找到进程"))

    if pid:
        uptime_s = run(f"ps -o etimes= -p {pid} 2>/dev/null || echo 0")
        try:
            sec = int(uptime_s.strip())
            days, rem = divmod(sec, 86400); hr, rem2 = divmod(rem, 3600); mn = rem2//60
            up_str = f"{days}d {hr}h {mn}m"
            kv("运行时长", up_str, "green")
        except:
            pass

    # 内存占用
    mem_rss = run(f"ps -o rss= -p {pid} 2>/dev/null || echo 0")
    if mem_rss:
        mb = int(mem_rss.strip()) / 1024
        cond = "red" if mb > 2048 else ("yellow" if mb > 1024 else "green")
        kv("内存占用", f"{mb:.0f} MB", cond)

    # 会话数
    sessions = run("ls /home/ubuntu/.hermes/sessions/ 2>/dev/null | wc -l")
    kv("会话数", sessions if sessions else "0")

    # 缓存大小
    cache = run("du -sh /home/ubuntu/.hermes/cache/ 2>/dev/null | cut -f1")
    kv("缓存", cache if cache else "N/A")

# ═══════════════════════════════════════════════════════════════
# 14. 巡检总结
# ═══════════════════════════════════════════════════════════════
def summary(oci_cost, resources, all_ok, model_results):
    section("十四、巡检总结")
    alerts = []

    if oci_cost > 0.05:
        alerts.append(fail(f"OCI 有新增费用 ${oci_cost:.4f}"))
    if resources.get("mem",0) > 85:
        alerts.append(fail(f"内存使用率 {resources['mem']}% 过高"))
    if resources.get("disk",0) > 85:
        alerts.append(fail(f"磁盘使用率 {resources['disk']}% 过高"))
    if not all_ok:
        alerts.append(fail("部分服务已停止"))

    # 模型不可用
    for name, code, _ in (model_results or []):
        if code != "200":
            alerts.append(warn(f"模型 {name} HTTP {code}"))

    if alerts:
        print(f"  {fail('⚠️  需要关注:')}")
        for a in alerts:
            print(f"    {a}")
    else:
        print(f"  {ok('✅  所有检查项正常')}")

    print(f"\n  ℹ️  报告生成时间: {TS}")
    print(f"  ℹ️  下一期: 明日 09:00 CST")
    print(BIG)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    print(f"\n{' '*20}{C}{BOLD}全局巡检报告 v3  {NOW.strftime('%Y-%m-%d')}{RESET}")
    print(f"{' '*10}{B}法立福 OCI 免费机 · {TS}{RESET}")

    # 读历史
    hist = read_history()

    # 1-14
    oci_cost    = check_oci_cost(hist)
    resources   = check_resources(hist)
    all_ok      = check_services()
    check_network()
    check_cron()
    check_backup()
    check_security()
    model_res   = check_models()
    check_azure()
    check_mcp()
    check_updates()
    check_logs()
    check_hermes()
    summary(oci_cost, resources, all_ok, model_res)

    # 写历史
    write_history({
        "oci_cost": oci_cost,
        "mem_pct":  resources.get("mem",0),
        "disk_pct": resources.get("disk",0),
        "date": DATE
    })

if __name__ == "__main__":
    main()
