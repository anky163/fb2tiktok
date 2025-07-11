# tiktok_uploader/utils.py

import json
import os
from pathlib import Path

COOKIE_PATH = os.path.join("cookies/tiktok_cookies.json")

def load_cookies():
    """
    Đọc và trả về cookie từ file tiktok_cookies.json
    """
    path = Path(COOKIE_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Cookie file không tồn tại: {COOKIE_PATH}")
    with open(path, "r") as f:
        cookies = json.load(f)
    return cookies

def print_log(msg):
    """
    In log chuẩn hóa kèm prefix [Uploader]
    """
    print(f"[Uploader] {msg}")
