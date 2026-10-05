#!/usr/bin/env python3
"""Them 1 san pham vao products.js tu link affiliate Shopee.

  python add.py "<link>" -c ao [-t ten] [-d mo-ta] [-i anh] [--expect-item ID] [--push]

--expect-item  = id san pham tren trang offer (vd 40604188350). Script moi link
                 affiliate ra URL that roi doi chieu id, bat truong hop copy nham link.
--dry-run      = chi kiem tra, khong ghi vao products.js.

Khi them NHIEU link: nghi 2-3s giua cac lan goi (Shopee de chan neu goi don dap).
"""
import argparse, html, re, subprocess, sys, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
CATS = ("ao", "quan", "fullset")
IMG_OK = re.compile(r"^https://[\w-]+\.img\.susercontent\.com/")
NUM_RE = re.compile(r"\d{6,}")


def die(msg):
    print(f"[x] {msg}", file=sys.stderr)
    sys.exit(1)


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


def resolve(url):
    """URL cuoi cung sau redirect - dung de doi chieu link affiliate."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.geturl()


def check_link(url, expect_item, verified):
    """Doi chieu link affiliate voi id san pham mong doi."""
    if not expect_item:
        print("[!] khong co --expect-item: KHONG doi chieu duoc link, tu kiem tra tay", file=sys.stderr)
        return
    try:
        final = resolve(url)
        verified[0] = True
    except Exception as e:
        die(f"khong mo duoc link de doi chieu ({e}). Dung --no-verify neu chac chan dung.")
    nums = set(NUM_RE.findall(final.split("?")[0]))
    if expect_item not in nums:
        die(f"LINK SAI: id {expect_item} khong co trong {final.split('?')[0]}\n"
            f"    id tim thay: {sorted(nums) or 'khong co'}")
    print(f"  [ok] doi chieu link: id {expect_item} khop")


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
    ap.add_argument("-d", "--desc", default="", help="mo ta phu hien duoi ten")
    ap.add_argument("-i", "--img", default="")
    ap.add_argument("--expect-item", default="", help="id san pham de doi chieu link")
    ap.add_argument("--no-verify", action="store_true", help="bo qua doi chieu link")
    ap.add_argument("--dry-run", action="store_true", help="chi kiem tra, khong ghi")
    ap.add_argument("--push", action="store_true", help="git commit + push sau khi them")
    a = ap.parse_args()

    src = open("products.js", encoding="utf-8").read()

    verified = [False]
    if not a.no_verify:
        check_link(a.url, a.expect_item, verified)

    # ten / anh: uu tien tham so tay, fallback og: tags
    title, img = "", ""
    try:
        title, img = og(a.url)
    except Exception as e:
        print(f"[!] khong lay duoc og tags ({e}) - phai nhap -t / -i", file=sys.stderr)

    p = {"c": a.cat, "t": a.title or title or "", "s": a.desc, "i": a.img or img, "l": a.url}

    if not p["t"]:
        die("thieu ten san pham (--title)")
    if not IMG_OK.match(p["i"] or ""):
        print(f"[!] anh khong phai CDN Shopee: {p['i'][:70] or '(trong)'}", file=sys.stderr)

    print("  ten:", p["t"][:60])
    print("  anh:", p["i"][:80] or "(trong)")

    if a.dry_run:
        print("  [ok] dry-run, khong ghi gi")
        return

    if f'l:"{a.url}"' in src:
        die("link nay da co trong products.js")

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
