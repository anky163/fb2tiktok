# fucktiktok/uploader.py – tự động đăng video lên TikTok bằng Playwright

"""
uploader.py – Tự động đăng video lên TikTok bằng Playwright

📦 Cách chạy:
    python3 -m fucktiktok.uploader --file path/to/video.mp4 [--caption "ghi chú"] [--cookies path/to/cookie.json]

🔧 Tham số:
    --file      Đường dẫn tới file video (.mp4) bắt buộc
    --caption   Caption TikTok (mặc định rỗng)
    --cookies   File cookie TikTok (mặc định: tiktok_cookies.json trong thư mục gốc)

📁 Cấu trúc project yêu cầu:
    fb2tiktok/
    ├── fucktiktok/
    │   ├── uploader.py
    │   ├── humanizer.py (optional)
    │   └── ...
    ├── video_cache/
    ├── logs/
    │   ├── history.log
    │   └── error.log
    └── tiktok_cookies.json

🛠 Lưu ý:
    - Cookie TikTok phải hợp lệ, đã đăng nhập từ trước
    - Nếu có `humanizer.py`, module sẽ tự gọi để giả lập thao tác người dùng
    - Không nên upload liên tục quá nhanh, tránh bị flag bot

🚧 TODO:
    - Retry khi đăng fail
    - Kiểm tra trạng thái đăng thành công thật sự
    - Thêm chọn ảnh bìa, tag...
"""

import os
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# === Constants ===
ROOT = Path(__file__).resolve().parent.parent  # fb2tiktok/
VIDEO_DIR = ROOT / "video_cache"
LOG_FILE = ROOT / "logs" / "history.log"
ERROR_FILE = ROOT / "logs" / "error.log"
DEFAULT_COOKIE = ROOT / "tiktok_cookies.json"

# === Logging ===
def log(msg, error=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    (ERROR_FILE if error else LOG_FILE).parent.mkdir(exist_ok=True, parents=True)
    with open(ERROR_FILE if error else LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")

# === Upload chính ===
async def upload_video(video_path: str, caption: str = "", cookie_file: str = str(DEFAULT_COOKIE)):
    video_path = Path(video_path)
    if not video_path.exists():
        log(f"❌ Không tìm thấy file video: {video_path}", error=True)
        return

    log(f"🚀 Bắt đầu upload: {video_path.name}")
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(ROOT / ".tiktok_profile"),
            headless=False
        )
        page = await browser.new_page()

        try:
            await page.goto("https://www.tiktok.com/upload", timeout=60000)
            await asyncio.sleep(3)

            # === Upload file ===
            input_elem = await page.wait_for_selector("input[type=file]", timeout=30000)
            await input_elem.set_input_files(str(video_path))
            log(f"📁 Đã chọn file: {video_path.name}")

            # === Fake hành vi người dùng (nếu có) ===
            try:
                from fucktiktok.humanizer import behave_like_human
                await behave_like_human(page, phase="mid_upload")
            except Exception as e:
                log(f"[WARN] Không thể fake người: {e}")

            # === Điền caption nếu có ===
            if caption:
                textarea = await page.query_selector("textarea[placeholder*='Miêu tả']")
                if textarea:
                    await textarea.fill(caption)
                    log("✏️  Đã điền caption.")

            # === Bấm nút Đăng ===
            post_btn = await page.wait_for_selector("button:has-text('Đăng')", timeout=30000)
            await post_btn.click()
            log(f"✅ ĐĂNG THÀNH CÔNG: {video_path.name}")

            await asyncio.sleep(10)
        except PlaywrightTimeout:
            log("⏰ Timeout khi chờ selector TikTok", error=True)
        except Exception as e:
            log(f"💥 Lỗi khi upload: {e}", error=True)
        finally:
            await browser.close()

# === CLI entry ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Đăng video lên TikTok qua Playwright.")
    parser.add_argument("--file", required=True, help="Đường dẫn video (.mp4)")
    parser.add_argument("--caption", default="", help="Caption cho video")
    parser.add_argument("--cookies", default=str(DEFAULT_COOKIE), help="Path cookie TikTok (json)")

    args = parser.parse_args()
    asyncio.run(upload_video(args.file, args.caption, args.cookies))
