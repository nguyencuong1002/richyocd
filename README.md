# Richyocd — link bio affiliate

**Live:** https://nguyencuong1002.github.io/richyocd/
**Repo:** https://github.com/nguyencuong1002/richyocd

Static, không build, không JS framework. GitHub Pages, branch `main`, thư mục `/`.

## Thêm sản phẩm

```bash
python add.py "https://s.shopee.vn/xxxx" -c quan --push
```

Tự lấy ảnh + tên từ `og:title`/`og:image` của trang, thêm 1 dòng vào `products.csv`, rồi commit + push.
Shopee thường chặn bot → nhập tay:

```bash
python add.py "<link>" -c quan -t "Tên sản phẩm" -s "30k+" \
  -i "https://down-vn.img.susercontent.com/file/xxx.webp" --push
```

(Mở trang sản phẩm trên Shopee → chuột phải ảnh → Copy image address.)

### Lấy link + ảnh + lượt bán từ Shopee Affiliate (cần Chrome đã đăng nhập)

Trang affiliate chặn bot nên `add.py` không tự lấy được `og:` tags. Lấy tay 4 giá trị:

1. Mở `https://affiliate.shopee.vn/offer/product_offer/<id>` trong Chrome
2. Bấm **Lấy link** → **Sao chép Link** → dán vào link
3. Chuột phải ảnh thumbnail → **Copy image address** → dán vào `-i`
4. Tên: copy dòng tiêu đề trên trang · Lượt bán: copy chỗ "30k+ lượt bán" → `-s`

Rồi chạy:

```bash
python add.py "<link affiliate>" -c ao \
  -t "Tên sản phẩm" -d "Mô tả phụ" -s "30k+" \
  -i "https://down-vn.img.susercontent.com/..." \
  --expect-item 40604188350 --push
```

Không cần `-t`/`-i` nếu dùng link Shopee thường (không phải link affiliate) — khi đó script tự lấy.

### Quy tắc khi làm nhiều link

- **Nghỉ 2–3s giữa các link.** Gọi dồn dập dễ bị Shopee chặn.
- **Luôn truyền `--expect-item <id>`** (id trên URL trang offer). Script mở link ra URL thật rồi đối chiếu id — bắt được trường hợp copy nhầm/thiếu ký tự.
- **Chạy `--dry-run` trước** khi ghi thật, để xem tên/ảnh/link có đúng không.
- Script tự chặn: link không mở được, id không khớp, thiếu tên, link đã có trong `products.csv`.
- Cảnh báo (không chặn): ảnh không thuộc CDN `*.img.susercontent.com`.

### File dữ liệu

`products.csv` — 1 dòng 1 sản phẩm, ô nào chứa dấu phẩy thì bọc trong `"..."` (script tự làm):

```
cat,title,desc,img,link,sold
ao,Tên sản phẩm,Mô tả phụ,https://...webp,https://s.shopee.vn/xxx,30k+
```

`cat` = `ao` | `quan` | `fullset`. `sold` để trống thì thẻ không hiện chip "đã bán".

Trang đọc CSV bằng `fetch` lúc tải → **phải chạy qua http**, mở trực tiếp `file://` sẽ báo lỗi.
Sau này muốn chuyển sang database thì chỉ cần `add.py` ghi vào DB và cho trang đọc từ API,
phần hiển thị không phải sửa.

Tên (`t`) tự động về **Title Case** khi hiển thị — cứ gõ tự nhiên, không cần chỉnh tay.
Mã/từ viết tắt (`GSM`, `XL`, `XXL`, `XS`, `NB`) và số dính chữ (`280GSM`) được giữ nguyên.

## Sửa trang

- Tên + link social: `index.html`, thẻ `<header>`.
- Avatar: file `avatar.png` (150×150) cạnh `index.html`.

## Xem thử tại máy

```bash
python -m http.server 8765
```
rồi mở http://127.0.0.1:8765
