# fb_downloader.py

import json
import subprocess
import os
from datetime import datetime
from facebook_video_downloader.utils import json_to_netscape, get_video_metadata


# === Config ==========================================

# Thư mục chứa video tải về
VIDEO_DIR = os.path.join("video_cache")

# File cookie Facebook dạng JSON (Playwright export)
COOKIE_JSON = os.path.join("cookies/facebook_cookies.json")

# File tạm để lưu cookie theo định dạng Netscape
TEMP_COOKIE_TXT = os.path.join("cookie_tmp.txt")

# File log lịch sử thành công, lỗi và ID các video đã tồn tại trong video_cache
LOG_FILE = os.path.join("logs/history.log")
ERROR_LOG = os.path.join("logs/error.log")
DOWNLOADED = os.path.join("logs/downloaded.json")


# ==========================================================================


def update_downloaded_log(video_id, caption="", timestamp=None):
    """
    Ghi video_id, caption, timestamp vào logs/downloaded.json.
    Nếu đã có → bỏ qua.
    """
    data = {}
    try:
        if os.path.exists(DOWNLOADED):
            with open(DOWNLOADED, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
    except Exception as e:
        log_error(f"⚠️ File downloaded.json lỗi JSON: {e}")

    if video_id not in data:
        data[video_id] = {
            "caption": caption,
            "timestamp": timestamp
        }

        try:
            with open(DOWNLOADED, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log(f"📝 Ghi vào downloaded.json: {video_id}")
        except Exception as e:
            log_error(f"❌ Không ghi được downloaded.json: {e}")



def log(msg):
    """Ghi log bình thường ra file history và console"""
    time_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{time_str} {msg}\n")
    print(msg)

def log_error(msg):
    """Ghi log lỗi ra file error và console"""
    time_str = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(ERROR_LOG, "a") as f:
        f.write(f"{time_str} {msg}\n")
    print("❌", msg)

def download_video(video_url, metadata=None):
    """
    Nếu metadata được truyền từ watcher, không cần móc lại.
    """
    video_id = "".join(c if c.isalnum() else "_" for c in video_url.split("/")[-1])[:40]
    output_path = os.path.join(VIDEO_DIR, f"{video_id}.mp4")
    os.makedirs(VIDEO_DIR, exist_ok=True)

    if os.path.exists(output_path):
        log(f"⚠️ Video đã tồn tại: {output_path}")
        return

    json_to_netscape(COOKIE_JSON, TEMP_COOKIE_TXT)

    cmd = [
        "yt-dlp",
        "--cookies", TEMP_COOKIE_TXT,
        "-o", output_path,
        video_url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(f"[DEBUG] yt-dlp exit code: {result.returncode}")
    print(f"[DEBUG] File tồn tại sau tải? {os.path.exists(output_path)}")
    print(f"[DEBUG] Đường dẫn file: {output_path}")

    if result.returncode == 0 and os.path.exists(output_path):
        log(f"✅ Tải thành công: {video_url} -> {output_path}")

        # 👇 Móc metadata 
        if metadata is None:
            metadata = get_video_metadata(video_id, cookie_file=TEMP_COOKIE_TXT)
            
        if metadata:
            update_downloaded_log(
                video_id=metadata["video_id"],
                caption=metadata["title"],
                timestamp=metadata["upload_ts"] or metadata["timestamp"]
            )
        else:
            log_error(f"❌ Không lấy được metadata cho {video_id}")
    else:
        log_error(f"Lỗi khi tải {video_url}")
        log_error(f"stderr: {result.stderr.strip()}")


# Nếu chạy file này trực tiếp, test tải video
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fb_downloader.py <video_url>")
        sys.exit(1)

    url = sys.argv[1]
    download_video(url)
