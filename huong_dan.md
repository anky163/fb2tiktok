0. Đầu tiên, tạo folder cookies/ và video_cache: 
-  mkdir cookies
-  mkdir video_cache

1. Tạo môi trường ảo để cài các thư viện cần thiết
-  python3 -m venv venv

2. Chạy môi trường ảo
-  source venv/bin/activate

3. Cài đặt thư viện
-  pip install -r requirements.txt

4. Truy cập facebook thông qua bot để lấy cookies
-  python -m fucktiktok.humanizer --url "https://facebook.com/" --keep

5. Đăng nhập facebook qua cửa sổ được hiển thị, sau đó chờ thông báo dưới terminal:
✅ Đã load 9 cookies từ /home/k/fb2tiktok/cookies/facebook_cookies.json
✅ Lưu 1 cookies → /home/k/fb2tiktok/cookies/google_cookies.json
✅ Lưu 32 cookies → /home/k/fb2tiktok/cookies/tiktok_cookies.json
✅ Lưu 1 cookies → /home/k/fb2tiktok/cookies/byteoversea_cookies.json
✅ Lưu 9 cookies → /home/k/fb2tiktok/cookies/facebook_cookies.json
💾 Đã lưu storage cho facebook → cookies/facebook_local.json
✅ Đã xử lý xong toàn bộ URL
🟢 Giữ trình duyệt mở. CTRL+C để thoát.

6. Đăng nhập facebook cho trình tải video (cho chắc, nếu nó duyệt đăng nhập rồi thì thôi)
-  python3 login_facebook.py

5. Dán đường link fanpage muốn theo dõi vào pages.txt, ví dụ: https://www.facebook.com/nguyen.uc.an.ky/

6. Chạy watcher để theo dõi và tải các videos mới nhất
-  python3 -m facebook_video_downloader.watcher-3-stealth

### Video tải về được lưu ở thư mục video_cache, thông tin nằm ở logs/downloaded.json