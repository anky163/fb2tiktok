# FB_STALKER

Một con bot theo dõi fanpage Facebook, tự động tải các video và reel mới nhất.

---

## 🚀 Cách sử dụng

### 1. Cài đặt thư viện cần thiết

pip install -r requirements.txt


---

### 2. Đăng nhập Facebook (1 lần duy nhất)


python login_facebook.py


- Một cửa sổ trình duyệt sẽ mở ra.
- **Đăng nhập Facebook bằng tay**
- Sau khi vào được Facebook, **bấm vào trang chủ / newfeed / avatar**, đợi tầm vài giây để load đủ cookies.
- Sau đó tắt trình duyệt → cookies và profile sẽ được lưu lại ở:
  - `cookies/facebook_cookies.json`
  - `cookies/facebook_profile/`
  - `netscape/facebook_cookies_netscape.txt`

---

### 3. Thêm danh sách fanpage cần theo dõi

Mở file `pages.txt`, dán mỗi link fanpage 1 dòng, ví dụ:


https://www.facebook.com/nguyen.uc.an.ky/
https://www.facebook.com/Amwaydepkhoe/


---

### 4. Khởi chạy stalker


python manager.py


- Mỗi fanpage sẽ được theo dõi bởi một `stalker.py` độc lập
- Mỗi stalker sẽ kiểm tra 3 post mới nhất trên fanpage đó
- Nếu phát hiện **video** hoặc **reel** mới chưa từng tải → tự động gọi downloader

---

## 📂 Cấu trúc thư mục


FB_STALKER/
├── fb_vid.py              # Tải video thường
├── fb_reel.py             # Tải reel
├── stalker.py             # Theo dõi 1 fanpage
├── manager.py             # Theo dõi nhiều fanpage
├── login_facebook.py      # Login và dump cookies
├── pages.txt              # Danh sách fanpage
├── history/
│   └── video_history.json # Lưu video_id đã tải
├── videos/                # Video tải về
├── cookies/
│   ├── facebook_cookies.json
│   ├── facebook_profile/
├── netscape/
│   └── facebook_cookies_netscape.txt
├── config.py
└── requirements.txt


---

## 🐾 Ghi chú

- `video_history.json` dùng để tránh tải trùng video
- `stalker.py` chạy vòng lặp vĩnh viễn, mỗi vòng cách nhau ~60s
- Có thể mở rộng bằng `manager.py` + log riêng từng stalker

---

Gâu.