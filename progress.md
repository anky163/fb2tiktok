# 📦 Dự án `fb2tiktok`
**Tự động theo dõi Fanpage Facebook → tải video mới → đăng lên TikTok**

---

## ✅ Tiến độ triển khai

### 🔹 **Giai đoạn 1 – Khởi tạo cấu trúc dự án**
- [x] Tạo thư mục `fb2tiktok/` chứa các module chức năng.
- [x] Tạo `pages.txt` – danh sách fanpage theo dõi.
- [x] Tạo `cookies.txt` – file cookie Facebook (dạng chuỗi `c_user=...; xs=...`)
- [x] Tạo folder `video_cache/` để lưu video.
- [x] Tạo folder `logs/` để log hoạt động (`history.log`, `error.log`).

---

### 🔹 **Giai đoạn 2 – Cào video từ Fanpage**
- [x] Viết `watcher.py`: theo dõi fanpage định kỳ, phát hiện post mới chứa video.
- [x] Parse `cookies.txt` thành dict, tương thích với `facebook_scraper`.
- [x] Cơ chế tránh trùng lặp post bằng `logs/processed_ids.txt`.
- [x] Test thành công với page công khai như `tiemcaphecu`.

---

### 🔹 **Giai đoạn 3 – Tải video từ Facebook**
- [x] Viết `fb_downloader.py`: dùng `yt-dlp` để tải video theo URL.
- [x] Tự động lấy metadata để đặt tên file từ title/description.
- [x] Ghi log chi tiết tải thành công/thất bại.
- [x] Tích hợp tự động từ `watcher.py` → gọi `fb_downloader.py` khi phát hiện post mới.

---

### 🔹 **Giai đoạn 4 – Upload video lên TikTok**
- [x] Viết `uploader_tiktok.py` sử dụng **Playwright async**.
- [x] Giữ đăng nhập TikTok bằng `--user-data-dir=.tiktok_profile`.
- [x] Tự động mở `https://www.tiktok.com/upload`, chọn video, đăng bài.
- [x] Có delay và kiểm tra nút `Đăng`, ghi log khi upload thành công.

---

## 📌 Kết quả hiện tại:
> 🟢 **Hệ thống chạy hoàn toàn tự động**:  
Khi 1 fanpage đăng video mới → script sẽ **phát hiện**, **tải về**, và **đăng lên TikTok** mà không cần can thiệp tay.

---

## 📁 Cấu trúc project

```
fb2tiktok/
├── pages.txt               # Danh sách fanpage theo dõi
├── cookies.txt             # Cookie Facebook
├── config.json             # (chưa dùng) caption tùy biến
├── watcher.py              # Theo dõi post video mới
├── fb_downloader.py        # Tải video bằng yt-dlp
├── uploader_tiktok.py      # Upload video lên TikTok
├── manual_upload.py        # (optional) Upload bằng tay
├── login_cookie.py         # (optional) Hỗ trợ login cookie
├── video_cache/            # Thư mục lưu video tải về
└── logs/
    ├── history.log         # Nhật ký hoạt động
    ├── error.log           # Lỗi
    └── processed_ids.txt   # Các post_id đã xử lý
```

---

## 🚧 TODO tiếp theo (nếu muốn nâng cấp):
- [ ] Kiểm tra session TikTok còn hoạt động không trước khi upload.
- [ ] Gửi email/Telegram nếu upload lỗi.
- [ ] Cấu hình caption tự sinh từ bài viết Facebook.
- [ ] Lọc theo tag, caption, hoặc điều kiện tùy biến.
- [ ] Hỗ trợ chạy như systemd service hoặc Docker container.

---

## ✍ Ghi chú
- Cookie Facebook cần lấy từ **tài khoản đã login**, dạng chuỗi raw.
- TikTok login chỉ cần 1 lần bằng Playwright (lưu vào `.tiktok_profile`), sau đó script dùng lại.
- Phát hiện video = dựa vào `facebook_scraper` → không dùng API Facebook.