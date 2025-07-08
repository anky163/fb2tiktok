# fb_downloader.py – dùng yt-dlp để tải video từ post Facebook
import os
import sys
import subprocess
import json
from datetime import datetime

VIDEO_DIR = "video_cache"
LOG_FILE = "logs/history.log"
ERROR_FILE = "logs/error.log"
COOKIE_FILE = "cookies.txt"

# === Ghi log ===
def log(msg, error=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    with open(ERROR_FILE if error else LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")

# === Làm sạch title để dùng làm tên file ===
def sanitize(text):
    return text.replace("/", "_").replace("\\", "_").strip()[:100]

# === Tải video bằng yt-dlp ===
def download_facebook_video(url):
    try:
        os.makedirs(VIDEO_DIR, exist_ok=True)

        # === Đọc cookie từ cookies.txt ===
        if not os.path.exists(COOKIE_FILE):
            raise Exception("Không tìm thấy file cookies.txt")

        cookie_str = open(COOKIE_FILE).read().strip()
        if "=" not in cookie_str:
            raise Exception("cookies.txt không đúng định dạng (không chứa =)")

        # === Tạo file cookies_tmp.txt theo chuẩn Netscape cho yt-dlp ===
        temp_cookie_path = "cookies_tmp.txt"
        with open(temp_cookie_path, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            for part in cookie_str.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    f.write(f".facebook.com\tTRUE\t/\tTRUE\t0\t{k}\t{v}\n")

        # === Lấy metadata video ===
        info = subprocess.run([
            "yt-dlp",
            "--cookies", temp_cookie_path,
            "--dump-json",
            url
        ], capture_output=True, text=True, timeout=30)

        if info.returncode != 0:
            raise Exception(f"Không lấy được metadata: {info.stderr.strip()}")

        data = json.loads(info.stdout)
        raw_title = data.get("description") or data.get("title") or "video"
        title = sanitize(raw_title)
        filename_tpl = f"{VIDEO_DIR}/{title}.%(ext)s"

        # === Tải video ===
        log(f"[downloading...] {url}")
        result = subprocess.run([
            "yt-dlp",
            "--cookies", temp_cookie_path,
            "--merge-output-format", "mp4",
            "-o", filename_tpl,
            url
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            log(f"[DOWNLOADER] OK – {title}")
        else:
            log(f"[DOWNLOADER] FAIL – {url}\n{result.stderr}", error=True)

        os.remove(temp_cookie_path)

    except Exception as e:
        log(f"[DOWNLOADER] ERROR – {url}: {e}", error=True)

# === Main ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fb_downloader.py <facebook_video_url>")
        sys.exit(1)

    url = sys.argv[1]
    download_facebook_video(url)
