#!/usr/bin/env python3
"""Them 1 san pham vao products.csv tu link affiliate Shopee.

  python add.py "<link>" -c ao [-t ten] [-d mo-ta] [-i anh] [-s "30k+"] [--expect-item ID] [--push]

--expect-item  = id san pham tren trang offer (vd 40604188350). Script moi link
                 affiliate ra URL that roi doi chieu id, bat truong hop copy nham link.
--dry-run      = chi kiem tra, khong ghi vao products.csv.

Khi them NHIEU link: nghi 2-3s giua cac lan goi (Shopee de chan neu goi don dap).
"""
import argparse, html, os, re, subprocess, sys, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125 Safari/537.36"
CRAWLER_UA = "facebookexternalhit/1.1"
CATS = ("ao", "quan", "fullset")
CSV = "products.csv"
IMG_OK = re.compile(r"^https://[\w-]+\.img\.susercontent\.com/")
NUM_RE = re.compile(r"\d{6,}")


def die(msg):
    print(f"[x] {msg}", file=sys.stderr)
    sys.exit(1)


def og(url):
    """og:title / og:image.

    Thu UA crawler truoc: Shopee tra HTML SSR co the og: cho no, con UA browser
    thi chi tra shell React rong (khong co og: gi).
    """
    for ua in (CRAWLER_UA, UA):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "vi"})
            with urllib.request.urlopen(req, timeout=20) as r:
                page = r.read(600_000).decode("utf-8", "ignore")
        except Exception:
            continue

        def find(prop):
            m = re.search(rf'<meta[^>]+(?:property|name)=["\']{prop}["\'][^>]+content=["\']([^"\']+)', page, re.I)
            if not m:
                m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{prop}["\']', page, re.I)
            return html.unescape(m.group(1)) if m else ""

        img = find("og:image")
        if img:
            title = re.sub(r"\s*\|\s*Shopee(?:\s+Việt\s+Nam)?\s*$", "", find("og:title")).strip()
            return title, thumb(img)
    return "", ""


def thumb(url):
    """Ban resize cua CDN Shopee (10KB thay vi vai tram KB) - transform chinh chu."""
    return url + "@resize_w640_nl.webp" if IMG_OK.match(url or "") and "@" not in url else url


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


def csv_field(v):
    """Ghi 1 o CSV, quote khi can (ten san pham hay co dau phay)."""
    v = str(v or "").replace("\r", " ").replace("\n", " ").strip()
    return f'"{v.replace(chr(34), chr(34) * 2)}"' if any(c in v for c in ',"') else v


def csv_row(p):
    return ",".join(csv_field(p[k]) for k in ("c", "t", "s", "i", "l", "sold"))


HEADER = "cat,title,desc,img,link,sold\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-c", "--cat", required=True, choices=CATS)
    ap.add_argument("-t", "--title", default="")
    ap.add_argument("-d", "--desc", default="", help="mo ta phu hien duoi ten")
    ap.add_argument("-i", "--img", default="")
    ap.add_argument("-p", "--product-url", default="", help="link shopee.vn/product/... de lay anh khi link affiliate chan bot")
    ap.add_argument("-s", "--sold", default="", help="luot ban hien tren the, vd 30k+")
    ap.add_argument("--expect-item", default="", help="id san pham de doi chieu link")
    ap.add_argument("--no-verify", action="store_true", help="bo qua doi chieu link")
    ap.add_argument("--dry-run", action="store_true", help="chi kiem tra, khong ghi")
    ap.add_argument("--push", action="store_true", help="git commit + push sau khi them")
    a = ap.parse_args()

    src = open(CSV, encoding="utf-8").read() if os.path.exists(CSV) else HEADER

    verified = [False]
    if not a.no_verify:
        check_link(a.url, a.expect_item, verified)

    # ten / anh: uu tien tham so tay, fallback og: tags
    title, img = "", ""
    try:
        title, img = og(a.product_url or a.url)
    except Exception as e:
        print(f"[!] khong lay duoc og tags ({e}) - phai nhap -t / -i", file=sys.stderr)

    p = {"c": a.cat, "t": a.title or title or "", "s": a.desc,
         "i": a.img or img, "l": a.url, "sold": a.sold}

    if not p["t"]:
        die("thieu ten san pham (--title)")
    if not IMG_OK.match(p["i"] or ""):
        print(f"[!] anh khong phai CDN Shopee: {p['i'][:70] or '(trong)'}", file=sys.stderr)

    print("  ten :", p["t"][:60])
    print("  anh :", p["i"][:80] or "(trong)")
    print("  ban :", p["sold"] or "(trong)")

    if a.dry_run:
        print("  [ok] dry-run, khong ghi gi")
        return

    if a.url in src:
        die(f"link nay da co trong {CSV}")

    if not src.endswith("\n"):
        src += "\n"
    open(CSV, "w", encoding="utf-8").write(src + csv_row(p) + "\n")

    if a.push:
        subprocess.run(["git", "add", CSV], check=True)
        subprocess.run(["git", "commit", "-m", f"add: {p['t'][:50]}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("  -> pushed")


if __name__ == "__main__":
    main()
