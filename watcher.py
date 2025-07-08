# watcher.py – sử dụng facebook-scraper để phát hiện post chứa video
import os
import time
import subprocess
from datetime import datetime
from facebook_scraper import get_posts

# === Cấu hình ===
PAGES_FILE = "pages.txt"                    # Danh sách fanpage cần theo dõi
PROCESSED_FILE = "logs/processed_ids.txt"    # Ghi lại post_id đã xử lý
HISTORY_LOG = "logs/history.log"              # Log hoạt động bình thường
ERROR_LOG = "logs/error.log"                  # Log lỗi
COOKIE_FILE = "cookies.txt"                   # Cookie Facebook
CHECK_INTERVAL = 60  # seconds                # Chu kỳ kiểm tra

# === Tạo thư mục/log nếu chưa có ===
os.makedirs("logs", exist_ok=True)
if not os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "w") as f:
        pass

# === Ghi log ra file + in terminal ===
def log(msg, error=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    with open(ERROR_LOG if error else HISTORY_LOG, "a") as f:
        f.write(line)
    print(line, end="")

# === Đọc danh sách post_id đã xử lý để tránh lặp lại ===
def get_processed_ids():
    with open(PROCESSED_FILE) as f:
        return set(line.strip() for line in f if line.strip())

# === Lưu thêm post_id mới vào log ===
def save_processed_id(pid):
    with open(PROCESSED_FILE, "a") as f:
        f.write(pid + "\n")

# === Lấy tham số trong cookies.txt
def parse_cookie_string(cookie_str):
    cookies = {}
    for part in cookie_str.strip().split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k] = v
    return cookies

# === Cào post từ fanpage (1 page gần nhất), lọc ra post có video ===
def detect_video_posts(page_name, cookies_param):
    print(f"[DEBUG] page name: {page_name}")
    try:
        # Nếu cookies_param là path đến file
        if os.path.exists(cookies_param):
            with open(cookies_param) as f:
                raw_cookie = f.read().strip()
        else:
            raw_cookie = cookies_param

        # Parse thành dict
        cookie_dict = parse_cookie_string(raw_cookie)

        # print("[DEBUG] cookie_dict =", cookie_dict)

        posts = get_posts(page_name, cookies=cookie_dict, pages=3)

        found = []

        # 🧪 Inject video test (giả lập 1 post video mới chưa từng có)
        '''
        if page_name == "tiemcaphecu":
            found.append((
                f"FAKE_{int(time.time())}",  # post_id giả, random theo timestamp
                None, 
                "https://www.facebook.com/tiemcaphecu/videos/961861465851955"
            ))
            
        '''
        for post in posts:
            print("[DEBUG]", post.get("post_id"), post.get("video_id"), post.get("post_url"))
            if post.get("video") or post.get("video_id"):
                found.append((post["post_id"], post.get("video_id"), post.get("post_url")))
        return found

    except Exception as e:
        log(f"Error scraping {page_name}: {e}", error=True)
        return []


# === Vòng lặp chính ===
def main_loop():
    log("[Watcher] Bắt đầu theo dõi fanpage qua facebook-scraper")
    processed = get_processed_ids()

    while True:
        try:
            # Đọc danh sách page từ file
            with open(PAGES_FILE) as f:
                pages = [line.strip() for line in f if line.strip()]

            # Với mỗi page: quét post mới → nếu có video + chưa xử lý thì gọi downloader
            for page in pages:
                log(f"[Watcher]     Đang theo dõi {page}")
                vids = detect_video_posts(page, COOKIE_FILE)
                for pid, vid, url in vids:
                    if pid not in processed:
                        log(f"[MỚI]         {page} – {url or vid}")
                        subprocess.Popen(["python3", "fb_downloader.py", url or vid])
                        save_processed_id(pid)
                        processed.add(pid)

        except Exception as e:
            log(f"Unhandled error: {e}", error=True)

        time.sleep(CHECK_INTERVAL)

# === Chạy ===
if __name__ == "__main__":
    main_loop()
