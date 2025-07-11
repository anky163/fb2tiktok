# 📦 Dự án `fb2tiktok`

**Tự động theo dõi fanpage Facebook → tải video mới → đăng lên TikTok bằng bot trình duyệt**

---

## ✅ Tiến độ triển khai

### 🔹 **Giai đoạn 1 – Cấu trúc & chuẩn bị**

- [x] Tạo thư mục `fb2tiktok/` làm workspace chính.
- [x] Tạo `pages.txt`: danh sách fanpage cần theo dõi.
- [x] Tạo `video_cache/`: nơi lưu clip đã tải.
- [x] Tạo `logs/`: ghi lại các hoạt động (`history.log`, `error.log`).
- [x] Thiết lập môi trường `venv/`, cài đặt Playwright và yt-dlp.

---

### 🔹 **Giai đoạn 2 – Watcher: theo dõi fanpage**

- [x] `watcher.py`: quét fanpage định kỳ, phát hiện post mới có video.
- [x] Trích xuất URL và caption từ post.
- [x] Tránh trùng video nhờ `logs/downloaded.json`.
- [x] Chạy vô hạn trong vòng lặp, delay giữa các fanpage.

---

### 🔹 **Giai đoạn 3 – Download video từ Facebook**

- [x] `fb_downloader.py`: tải video từ post bằng `yt-dlp`.
- [x] Tự convert `fb_cookies.json` → `cookies_tmp.txt` (dạng Netscape cho yt-dlp).
- [x] Ghi log tải thành công/thất bại, kiểm tra lỗi cookie.
- [x] Gọi độc lập hoặc từ `watcher.py`.

---

### 🔹 **Giai đoạn 4 – Giả lập người dùng TikTok bằng bot**

- [x] `fucktiktok/humanizer.py`: mở trình duyệt Chrome thật, điều khiển như người.
- [x] Hover, paste caption, click upload → hoạt động ổn định.
- [x] Cookie đăng nhập TikTok được lưu ở `cookies/tiktok_cookies.json`, đủ giữ session lâu dài.
- [x] Inject script `stealth_patch-2.js` qua `stealth.py` để bypass anti-bot.
- [x] `tiktok_uploader/uploader.py` đạt milestone "debug sâu & phản xạ thật": thao tác y như người dùng thực, kiểm tra lỗi upload kỹ lưỡng, chỉ ghi log nếu upload thành công.

---

### 🔹 **Giai đoạn 5 – Quản lý cookie Facebook**

- [x] `login_facebook.py`: login tay, trích cookie TikTok/Facebook
- [x] Cookie lưu vào `cookies/facebook_cookies.json`

---

## 📁 Cấu trúc thực tế (tóm tắt)

fb2tiktok/
├── chrome_profiles/  # Profile trình duyệt theo mục đích (TikTok, Facebook...)
├── cookies/  # Tất cả cookie (TikTok, FB, Google, v.v.)
├── facebook_video_downloader/
│   ├── watcher-3-stealth.py
│   ├── fb_downloader.py
├── fucktiktok/
│   ├── uploader.py
│   ├── stealth.py, humanizer.py
├── tiktok_uploader/
│   ├── uploader.py, uploader-1.py, utils.py
├── logs/
├── video_cache/
├── tiktok_user_data/
├── login_tiktok_qr.py, login_facebook.py
├── pages.txt, config.json

---

## 📌 Kết quả hiện tại:

> ✅ **Đã có thể chạy thủ công toàn bộ pipeline:**
> 1. `watcher.py` phát hiện post mới  
> 2. `fb_downloader.py` tải video  
> 3. `uploader.py` mở trình duyệt thật, đăng lên TikTok  
>     Trình trạng: upload vẫn bị lỗi
> 4. Trình duyệt giữ mở để quan sát. Log kỹ cả toast lỗi.

> ⚠️ Chưa khép kín toàn bộ pipeline thành 1 script tự động từ A→Z  


---

## 🛠 TODO tiếp theo:

- [ ] Ghép watcher → downloader → uploader thành 1 flow duy nhất (`auto_uploader.py`)
- [ ] Fake tương tác chuột/phím nâng cao trong `humanizer.py`
- [ ] Retry khi upload thất bại, thêm alert/log riêng
- [ ] Cho phép caption tự sinh từ post Facebook hoặc filter video theo từ khóa
- [ ] Docker hóa hoặc tạo systemd service để chạy nền

---

## 🧠 Ghi chú kỹ thuật

- Không dùng API TikTok/Facebook → tránh toang do auth
- Cookie TikTok có thể giữ đăng nhập lâu dài nếu không bị xoá session thủ công
- Chỉ cần login QR 1 lần, lưu `tiktok_cookies.json` là đủ
- Upload TikTok bằng **bot trình duyệt thật** → bám UI layout, dễ toang nếu TikTok đổi giao diện
