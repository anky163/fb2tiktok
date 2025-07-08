import json
import subprocess
import os
from datetime import datetime

# Thư mục chứa video tải về
VIDEO_DIR = "video_cache"

# File cookie Facebook dạng JSON (Playwright export)
COOKIE_JSON = "fb_cookies.json"

# File tạm để lưu cookie theo định dạng Netscape
TEMP_COOKIE_TXT = "cookies_tmp.txt"

# File log lịch sử thành công và lỗi
LOG_FILE = "logs/history.log"
ERROR_LOG = "logs/error.log"

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

def json_to_netscape(json_path, txt_path):
    """
    Chuyển file cookie JSON (Playwright) sang định dạng Netscape dùng cho yt-dlp
    """
    with open(json_path, "r") as f:
        cookies = json.load(f)

    lines = ["# Netscape HTTP Cookie File"]
    for c in cookies:
        domain = c.get("domain", ".facebook.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        expiry = str(c.get("expires", 9999999999))
        name = c["name"]
        value = c["value"]
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}")

    with open(txt_path, "w") as f:
        f.write("\n".join(lines) + "\n")

def download_video(video_url):
    """
    Tải video Facebook từ URL bằng yt-dlp, sử dụng cookie hợp lệ.
    Kiểm tra tồn tại file, log chi tiết.
    """
    # Chuẩn bị tên file video theo phần cuối URL, thay ký tự đặc biệt thành "_"
    video_id = "".join(c if c.isalnum() else "_" for c in video_url.split("/")[-1])[:40]
    output_path = os.path.join(VIDEO_DIR, f"{video_id}.mp4")

    # Tạo thư mục lưu video nếu chưa có
    os.makedirs(VIDEO_DIR, exist_ok=True)

    # Nếu file đã tồn tại, bỏ qua tải
    if os.path.exists(output_path):
        log(f"⚠️ Video đã tồn tại: {output_path}")
        return

    # Chuyển cookie JSON sang file Netscape để yt-dlp đọc được
    json_to_netscape(COOKIE_JSON, TEMP_COOKIE_TXT)

    # Lệnh yt-dlp với cookie, format tốt nhất, output file chỉ định
    cmd = [
        "yt-dlp",
        "--cookies", TEMP_COOKIE_TXT,
        "-f", "best",
        "-o", output_path,
        video_url
    ]

    # Chạy lệnh, lấy stdout, stderr
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Debug thông tin kết quả chạy
    print(f"[DEBUG] yt-dlp exit code: {result.returncode}")
    print(f"[DEBUG] File tồn tại sau tải? {os.path.exists(output_path)}")
    print(f"[DEBUG] Đường dẫn file: {output_path}")

    # Kiểm tra kết quả và file
    if result.returncode == 0 and os.path.exists(output_path):
        log(f"✅ Tải thành công: {video_url} -> {output_path}")
    else:
        log_error(f"Lỗi khi tải {video_url}")
        log_error(f"stderr: {result.stderr.strip()}")
        if "403" in result.stderr or "login" in result.stderr.lower():
            log_error("→ Có thể cookie Facebook đã hết hạn.")

# Nếu chạy file này trực tiếp, test tải video
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fb_downloader.py <video_url>")
        sys.exit(1)

    url = sys.argv[1]
    download_video(url)
