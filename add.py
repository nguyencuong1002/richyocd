#!/usr/bin/env python3
"""Them 1 san pham vao products.js tu link affiliate.

  python add.py "<link>" -c ao [-s "% giam"] [-t ten] [--push]

Tu lay anh + ten tu the og:image / og:title cua trang.
"""
import argparse, html, re, subprocess, sys, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
CATS = ("ao", "quan", "fullset")


def og(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi"})
    with urllib.request.urlopen(req, timeout=20) as r:
        page = r.read(400_000).decode("utf-8", "ignore")

    def find(prop):
        m = re.search(rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']+)', page, re.I)
        if not m:
            m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{prop}["\']', page, re.I)
        return html.unescape(m.group(1)) if m else ""

    return find("og:title"), find("og:image")


def js_line(p):
    parts = [f'c:"{p["c"]}"']
    for k in ("t", "s", "i", "l"):
        if p.get(k):
            parts.append(f'{k}:"{p[k].replace(chr(92), "").replace(chr(34), "")}"')
    return "  {" + ", ".join(parts) + "},"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-c", "--cat", required=True, choices=CATS)
    ap.add_argument("-t", "--title", default="")
    ap.add_argument("-i", "--img", default="")
    ap.add_argument("--push", action="store_true", help="git commit + push sau khi them")
    a = ap.parse_args()

    title, img = "", ""
    try:
        title, img = og(a.url)
    except Exception as e:
        print(f"[!] khong lay duoc og tags ({e}) - nhap tay bang -t / -i", file=sys.stderr)

    p = {
        "c": a.cat,
        "t": a.title or title or "(chua co ten)",
        "s": "",
        "i": a.img or img,
        "l": a.url,
    }
    print("  them:", p["t"][:60])
    print("  anh :", p["i"][:80] or "(trong)")

    src = open("products.js", encoding="utf-8").read()
    marker = "window.PRODUCTS = ["
    i = src.index(marker) + len(marker)
    open("products.js", "w", encoding="utf-8").write(src[:i] + "\n" + js_line(p) + src[i:])

    if a.push:
        subprocess.run(["git", "add", "products.js"], check=True)
        subprocess.run(["git", "commit", "-m", f"add: {p['t'][:50]}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("  -> pushed")


if __name__ == "__main__":
    main()
