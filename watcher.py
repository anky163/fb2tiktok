import os
import time
import subprocess
import json
from datetime import datetime
from facebook_scraper import get_posts

# === Cấu hình các file và tham số ===
PAGES_FILE = "pages.txt"                      # File danh sách fanpage cần theo dõi
PROCESSED_FILE = "logs/processed_ids.txt"    # File ghi lại các post_id đã xử lý tránh lặp lại
HISTORY_LOG = "logs/history.log"              # File log các hoạt động thành công
ERROR_LOG = "logs/error.log"                   # File log các lỗi phát sinh
COOKIE_JSON = "fb_cookies.json"                # File cookie Facebook dạng JSON (Playwright)
CHECK_INTERVAL = 60  # seconds                  # Khoảng thời gian giữa các lần check (giây)

# === Tạo thư mục và file log nếu chưa tồn tại ===
os.makedirs("logs", exist_ok=True)
if not os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "w") as f:
        pass  # Tạo file rỗng

def log(msg, error=False):
    """
    Hàm ghi log ra file và in ra console.
    Nếu error=True thì ghi vào file lỗi, ngược lại ghi vào file history.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    with open(ERROR_LOG if error else HISTORY_LOG, "a") as f:
        f.write(line)
    print(line, end="")

def get_processed_ids():
    """
    Đọc file PROCESSED_FILE để lấy tập post_id đã xử lý,
    giúp tránh tải lại video cũ.
    """
    with open(PROCESSED_FILE) as f:
        return set(line.strip() for line in f if line.strip())

def save_processed_id(pid):
    """
    Lưu post_id mới đã xử lý vào file để lần sau không tải lại.
    """
    with open(PROCESSED_FILE, "a") as f:
        f.write(pid + "\n")

def load_cookies_from_json(json_path):
    """
    Đọc file cookie JSON định dạng Playwright, chuyển sang dict dạng
    {cookie_name: cookie_value} để truyền cho facebook_scraper.
    """
    try:
        with open(json_path, "r") as f:
            cookies_json = json.load(f)
        cookies_dict = {c['name']: c['value'] for c in cookies_json}
        return cookies_dict
    except Exception as e:
        log(f"Failed to load cookies JSON: {e}", error=True)
        return {}

def detect_video_posts(page_name, cookie_dict):
    """
    Sử dụng facebook_scraper.get_posts để lấy các bài post từ fanpage,
    lọc ra các post có video, trả về list (post_id, video_id, video_url).
    Có đoạn inject thêm video giả để test.
    """
    print(f"[DEBUG] page name: {page_name}")
    try:
        posts = get_posts(page_name, cookies=cookie_dict, pages=3)
        found = []

        # Inject video test giả lập post video mới, tránh lỗi cache processed
        if page_name == "tiemcaphecu":
            found.append((
                f"FAKE_{int(time.time())}",  # post_id giả, mỗi lần khác nhau
                None,
                "https://www.facebook.com/tiemcaphecu/videos/961861465851955"
            ))

        # Duyệt các bài post lấy được, tìm video
        for post in posts:
            print("[DEBUG]", post.get("post_id"), post.get("video_id"), post.get("post_url"))
            if post.get("video") or post.get("video_id"):
                found.append((post["post_id"], post.get("video_id"), post.get("post_url")))
        return found

    except Exception as e:
        log(f"Error scraping {page_name}: {e}", error=True)
        return []

def main_loop():
    """
    Vòng lặp chính của watcher:
    - Load danh sách fanpage cần theo dõi
    - Load cookie Facebook dạng dict
    - Lặp vô hạn: kiểm tra post mới có video
    - Nếu phát hiện post mới chưa tải, gọi script downloader đồng bộ
      và chỉ lưu processed khi tải thành công.
    """
    log("[Watcher] Bắt đầu theo dõi fanpage qua facebook-scraper")
    processed = get_processed_ids()
    cookie_dict = load_cookies_from_json(COOKIE_JSON)

    if not cookie_dict:
        log("Cookie dict empty! Dừng watcher để kiểm tra lại cookie.", error=True)
        return

    while True:
        try:
            # Đọc danh sách fanpage từ file
            with open(PAGES_FILE) as f:
                pages = [line.strip() for line in f if line.strip()]

            # Quét từng fanpage
            for page in pages:
                log(f"[Watcher]     Đang theo dõi {page}")
                vids = detect_video_posts(page, cookie_dict)

                # Duyệt các post video phát hiện được
                for pid, vid, url in vids:
                    if pid not in processed:
                        log(f"[MỚI]         {page} – pid={pid}, url={url or vid}")
                        cmd = ["python3", "fb_downloader.py", url or vid]
                        try:
                            # Chạy downloader đồng bộ, timeout 300s
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                            if result.returncode == 0:
                                log(f"✅ Tải xong {url or vid}")
                                save_processed_id(pid)
                                processed.add(pid)
                            else:
                                log(f"❌ Lỗi tải video: {url or vid}")
                                log(f"stderr: {result.stderr.strip()}", error=True)
                        except subprocess.TimeoutExpired:
                            log(f"❌ Timeout tải video: {url or vid}", error=True)

        except Exception as e:
            log(f"Unhandled error: {e}", error=True)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
