# Richyocd — link bio affiliate

Static, không build, không JS framework. Chạy trên GitHub Pages (1 repo, branch `main`, thư mục `/`).

## Thêm sản phẩm

```bash
python add.py "https://shope.ee/xxxx" -c ao -s 15 --push
```

Tự lấy ảnh + tên từ `og:title`/`og:image` của trang, chèn lên đầu `products.js`, rồi commit + push.
Bỏ `-s` nếu không có badge giảm giá. Nếu trang chặn bot (không lấy được og) → nhập tay:

```bash
python add.py "<link>" -c quan -t "Tên sản phẩm" -i "https://.../anh.jpg"
```

Hoặc sửa thẳng `products.js`, mỗi sản phẩm 1 dòng:

```js
{c:"ao", t:"Tên", s:"mô tả phụ", i:"link ảnh", l:"link affiliate", d:"15"}
```

`c` = `ao` | `quan` | `fullset`.

## Sửa trang

- Tên + link social: `index.html`, thẻ `<header>`.
- Avatar: để file `avatar.jpg` cạnh `index.html`.

## Xem thử tại máy

```bash
python -m http.server 8765
```
rồi mở http://127.0.0.1:8765
