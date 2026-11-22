#!/usr/bin/env python3
"""TOTP 诊断工具：由 base32 setup key 生成 prev/current/next 三窗口码。

三窗口覆盖约 90 秒，用于和验证器 App 当前显示比对：
- App 显示三者之一 -> 密钥正确（拒绝原因在账号侧）
- 完全对不上     -> 密钥不是该账号注册的那把

用法（密钥走环境变量，避免进 shell history / 工具回显）:
    TOTP_SECRET=*** python3 totp.py

登录提交场景不要用本脚本跨进程传码（30 秒窗口+调用延迟易过期），
应把同样的生成逻辑内联进同一个 browser_exec 进程里生成->填入->提交。
"""
import base64
import hashlib
import hmac
import os
import struct
import sys
import time


def totp(key: bytes, counter: int) -> str:
    """RFC6238 标准 TOTP：SHA1 / 30s / 6 位（AWS 等主流站点通用）。"""
    h = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[o:o + 4])[0] & 0x7FFFFFFF) % 1000000:06d}"


def main() -> None:
    secret = os.environ.get("TOTP_SECRET", "").strip().replace(" ", "").upper()
    if not secret:
        sys.exit("请设置 TOTP_SECRET 环境变量（base32 setup key），不要把密钥写进命令行参数")
    # 兼容 otpauth:// URI 里 secret= 参数与缺 padding 的 base32
    if "SECRET=" in secret:
        secret = secret.split("SECRET=")[1].split("&")[0]
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))

    now = time.time()
    c = int(now) // 30
    print("host_UTC:", time.strftime("%H:%M:%S", time.gmtime(now)))
    print("prev   :", totp(key, c - 1))
    print("CURRENT:", totp(key, c), f"(还有 {30 - int(now % 30)}s 轮换)")
    print("next   :", totp(key, c + 1))


if __name__ == "__main__":
    main()
