# utils.py

import json
import os
import subprocess
from datetime import datetime
from playwright.sync_api import sync_playwright

# File mặc định
DEFAULT_DOWNLOADED_JSON = os.path.join("logs/downloaded.json")

def json_to_netscape(json_path, txt_path):
    """
    Convert Playwright cookie JSON → Netscape (dùng cho yt-dlp)
    """
    with open(json_path, "r") as f:
        cookies = json.load(f)

    lines = ["# Netscape HTTP Cookie File"]
    for c in cookies:
        domain = c.get("domain", ".facebook.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        raw_expiry = c.get("expires", 9999999999)
        try:
            expiry = str(int(float(raw_expiry)))
        except:
            expiry = "9999999999"
        name = c["name"]
        value = c["value"]
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}")

    with open(txt_path, "w") as f:
        f.write("\n".join(lines) + "\n")

def load_facebook_cookies(cookie_path):
    """
    Trả về list cookies dạng dict (dùng cho Playwright)
    """
    with open(cookie_path, "r") as f:
        raw = json.load(f)
    cookies = []
    for c in raw:
        if "facebook.com" in c.get("domain", ""):
            cookies.append({
                "name": c["name"],
                "value": c["value"],
                "domain": c["domain"],
                "path": c.get("path", "/"),
                "expires": -1,
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", False),
                "sameSite": "Lax",
            })
    return cookies

def load_downloaded_ids(path=DEFAULT_DOWNLOADED_JSON):
    """
    Trả về dict: {video_id: {"caption": ..., "timestamp": ...}}
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Lỗi load {path}: {e}")
        return {}

def upload_date_to_timestamp(date_str):
    """
    YYYYMMDD → Unix timestamp (int)
    """
    try:
        dt = datetime.strptime(date_str, "%Y%m%d")
        return int(dt.timestamp())
    except:
        return None

def get_video_metadata(video_id, cookie_file="cookies_tmp.txt"):
    """
    Trích metadata video Facebook qua yt-dlp
    Trả về dict: {
        video_id,
        timestamp,
        upload_date,
        upload_ts,
        modified_date,
        title
    }
    """
    url = f"https://www.facebook.com/watch/?v={video_id}"
    cmd = [
        "yt-dlp",
        "--cookies", cookie_file,
        "--no-warnings",
        "--print", "%(id)s|%(timestamp)s|%(upload_date)s|%(modified_date)s|%(title)s",
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = result.stdout.strip()
        if "|" in out:
            vid, ts, up, mod, title = out.split("|", 4)
            ts = int(ts) if ts.isdigit() else None
            upload_ts = upload_date_to_timestamp(up) if up else None

            return {
                "video_id": vid,
                "timestamp": ts,
                "upload_date": up or None,
                "upload_ts": upload_ts,
                "modified_date": mod or None,
                "title": title.strip()
            }
        
    except Exception as e:
        print(f"⚠️  Lỗi get_video_metadata {video_id}: {e}")
    return None
