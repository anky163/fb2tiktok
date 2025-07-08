# 📦 Dự án `fb2tiktok`

**Tự động theo dõi Fanpage Facebook → tải video mới → đăng lên TikTok**

---

## ✅ Tiến độ triển khai

### 🔹 **Giai đoạn 1 – Khởi tạo cấu trúc dự án**

* [x] Tạo thư mục `fb2tiktok/` chứa các module chức năng.
* [x] Tạo `pages.txt` – danh sách fanpage theo dõi.
* [x] Tạo `video_cache/` để lưu video tải về.
* [x] Tạo `logs/` để log hoạt động (`history.log`, `error.log`, `processed_ids.txt`).

---

### 🔹 **Giai đoạn 2 – Cào video từ Fanpage**

* [x] Viết `watcher.py`: theo dõi fanpage định kỳ, phát hiện post mới chứa video.
* [x] Đọc cookie từ `fb_cookies.json`, parse thành dict cho `facebook_scraper`.
* [x] Cơ chế tránh trùng lặp post bằng `logs/processed_ids.txt`.
* [x] Test thành công với page công khai như `tiemcaphecu`.

---

### 🔹 **Giai đoạn 3 – Tải video từ Facebook**

* [x] Viết `fb_downloader.py`: dùng `yt-dlp` để tải video theo URL.
* [x] Tự động convert `fb_cookies.json` thành `cookies_tmp.txt` (Netscape format).
* [x] Ghi log chi tiết tải thành công/thất bại, kiểm tra lỗi cookie.
* [x] Tích hợp từ `watcher.py` → gọi `fb_downloader.py` khi phát hiện post mới.

---

### 🔹 **Giai đoạn 4 – Upload video lên TikTok**

* [x] Viết `uploader_tiktok.py` sử dụng **Playwright async**.
* [x] Giữ đăng nhập TikTok bằng thư mục `tiktok_user_data/`.
* [x] Tự động mở `https://www.tiktok.com/upload`, chọn video, đăng bài.
* [x] Có delay và kiểm tra nút `Đăng`, ghi log khi upload thành công.

---

### 🔹 **Giai đoạn 5 – Quản lý cookie Facebook**

* [x] Module `fb_cookies_manager/` chia làm các file:

  * `login.py`: tự động login Facebook lưu `fb_cookies.json`
  * `auto.py`, `checker.py`, `utils.py`: dự kiến dùng cho việc kiểm tra/gia hạn
* [x] Có thể chạy `python -m fb_cookies_manager` hoặc `fb_cookie_manager_cli.py`
* [x] Hỗ trợ lấy lại cookie bằng tay 1 lần, sau đó dùng mãi

---

## 📁 Cấu trúc thư mục (thực tế)

```
fb2tiktok/
├── config.json                 # Chứa fb_user, fb_pass nếu dùng login tự động
├── fb_cookies.json             # Cookie Facebook định dạng JSON
├── cookies_tmp.txt            # Bản tạm Netscape cho yt-dlp
├── fb_cookies_manager/        # Module quản lý cookie FB
│   ├── login.py               # Tự động login Facebook
│   ├── auto.py                # (chưa dùng)
│   ├── checker.py             # (chưa dùng)
│   ├── utils.py               # (trống)
│   └── __main__.py
├── fb_cookie_manager_cli.py   # CLI chạy nhanh quản lý cookie
├── fb_downloader.py           # Dùng yt-dlp tải video
├── uploader_tiktok.py         # Upload video lên TikTok
├── manual_upload.py           # Upload TikTok bằng tay nếu cần
├── login_cookie.py            # Legacy script hỗ trợ login
├── watcher.py                 # Theo dõi fanpage và gọi downloader
├── logs/
│   ├── history.log
│   ├── error.log
│   └── processed_ids.txt
├── pages.txt                  # Danh sách fanpage
├── video_cache/               # Lưu video đã tải
├── tiktok_user_data/          # Dữ liệu trình duyệt TikTok
└── venv/                      # Virtual environment
```

---

## 📌 Kết quả hiện tại:

> 🟢 **Hệ thống chạy hoàn toàn tự động**:
> Khi một fanpage đăng video mới → script sẽ **phát hiện**, **tải về**, và **đăng lên TikTok** mà không cần can thiệp tay.

---

## 🚧 TODO tiếp theo:

* [ ] Kiểm tra session TikTok còn hoạt động không trước khi upload.
* [ ] Gửi email/Telegram nếu upload lỗi.
* [ ] Cấu hình caption tự sinh từ bài viết Facebook.
* [ ] Lọc theo tag, caption, hoặc điều kiện tùy biến.
* [ ] Hỗ trợ chạy như systemd service hoặc Docker container.

---

## ✍ Ghi chú

* Cookie Facebook cần lấy từ tài khoản đã login, dạng JSON (`fb_cookies.json`).
* TikTok chỉ cần login 1 lần bằng Playwright (đã lưu session).
* Phát hiện video dùng `facebook_scraper`, không gọi API chính thức.
