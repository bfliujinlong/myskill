#!/usr/bin/env python3
"""CodeBuddy CLI PTY login helper.

Runs `codebuddy login` in a pseudo-terminal, auto-confirms the trust-folder
prompt, selects 'Log in via Chinese Site', and extracts the full login URL.
The URL is printed to stdout for the caller to forward to the user.

Usage:
    python3 codebuddy-pty-login.py

Requirements:
    - codebuddy CLI installed and on PATH (~/.npm-global/bin/codebuddy)
    - Run on the VM where codebuddy should be authenticated
"""
import pty, os, sys, time, select, re, struct, fcntl, termios


def set_winsize(fd, rows=50, cols=200):
    """Set PTY window size wide enough to avoid URL truncation."""
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_output(fd, timeout=10):
    output = b''
    start = time.time()
    while time.time() - start < timeout:
        r, _, _ = select.select([fd], [], [], 0.3)
        if r:
            try:
                data = os.read(fd, 16384)
                if data:
                    output += data
            except OSError:
                break
    return output


def main():
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(os.path.expanduser('~'))
        os.execvp('codebuddy', ['codebuddy', 'login'])
    else:
        set_winsize(fd, 50, 200)

        # Wait for trust-folder prompt
        read_output(fd, 6)
        # Confirm default selection (option 1) with Enter
        os.write(fd, b'\r')
        read_output(fd, 5)
        # Select 'Log in via Chinese Site' (already selected, press Enter)
        os.write(fd, b'\r')
        # Wait for URL to appear in output
        out = read_output(fd, 20)
        text = out.decode('utf-8', errors='replace')

        # Extract unique login URLs
        urls = re.findall(r'https://copilot\.tencent\.com/login\?\S+', text)
        if urls:
            url = max(set(urls), key=len)
            print(url)
            sys.exit(0)
        else:
            print('ERROR: No login URL found', file=sys.stderr)
            print(text[:2000], file=sys.stderr)
            sys.exit(1)
        os.kill(pid, 9)


if __name__ == '__main__':
    main()
