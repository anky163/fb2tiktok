import os
import json
import sys
import yt_dlp
from config import VIDEO_DIR, COOKIES_PATH, HISTORY_FILE, NETSCAPE_DIR, convert_json_to_netscape, save_metadata_to_history

NETSCAPE = os.path.join(NETSCAPE_DIR, "facebook_cookies_netscape.txt")

def extract_video_id_from_url(url: str) -> str:
    """
    Trích ID từ URL reel, ví dụ:
    https://www.facebook.com/reel/660626140351530 → "660626140351530"
    """
    parts = url.rstrip('/').split('/')
    return parts[-1] if parts[-1].isdigit() else None

def download_reel(url):
    history = []

    # Đảm bảo cookies Netscape tồn tại
    if not os.path.exists(NETSCAPE):
        print(f"⚠️ Chưa có {NETSCAPE}, đang convert từ JSON...\n")
        convert_json_to_netscape(COOKIES_PATH, NETSCAPE)

    video_id = extract_video_id_from_url(url)
    if not video_id:
        print("❌ Không trích được video_id từ URL.\n")
        return

    # print(f"🎯 video_id: {video_id}\n")

    # Dò lịch sử download
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
    existing_ids = {item.get("video_id") for item in history}

    # Nếu video đã có sẵn, bỏ qua
    if video_id in existing_ids:
        # print(f"⚠️ Video {video_id} đã tồn tại trong lịch sử. Bỏ qua tải lại.\n")
        return

    ydl_opts = {
        'outtmpl': os.path.join(VIDEO_DIR, f'{video_id}.%(ext)s'),
        'cookiefile': NETSCAPE,
        'merge_output_format': 'mp4',
        'format': 'best',
        'quiet': False,
        'noplaylist': True,
        'progress_with_newline': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            metadata = {
                "video_id": video_id,
                "title": info.get("title"),
                "description": info.get("description"),
                "upload_date": info.get("upload_date")
            }
            save_metadata_to_history(metadata)

    except Exception as e:
        print(f"❌ Lỗi khi tải reel: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ usage: python fb_reel.py <facebook_reel_url>")
        sys.exit(1)

    os.makedirs(VIDEO_DIR, exist_ok=True)
    download_reel(sys.argv[1])
