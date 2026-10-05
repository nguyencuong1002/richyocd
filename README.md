# Richyocd — link bio affiliate

**Live:** https://nguyencuong1002.github.io/richyocd/
**Repo:** https://github.com/nguyencuong1002/richyocd

Static, không build, không JS framework. GitHub Pages, branch `main`, thư mục `/`.

## Thêm sản phẩm

```bash
python add.py "https://s.shopee.vn/xxxx" -c quan --push
```

Tự lấy ảnh + tên từ `og:title`/`og:image` của trang, chèn lên đầu `products.js`, rồi commit + push.
Shopee thường chặn bot → nhập tay:

```bash
python add.py "<link>" -c quan -t "Tên sản phẩm" \
  -i "https://down-vn.img.susercontent.com/file/xxx.webp" --push
```

(Mở trang sản phẩm trên Shopee → chuột phải ảnh → Copy image address.)

Hoặc sửa thẳng `products.js`, mỗi sản phẩm 1 dòng:

```js
{c:"ao", t:"Tên", s:"mô tả phụ", i:"link ảnh", l:"link affiliate"}
```

`c` = `ao` | `quan` | `fullset`.

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
