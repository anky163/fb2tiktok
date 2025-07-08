# uploader_tiktok.py – tự động đăng video lên TikTok bằng Playwright
import asyncio
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

VIDEO_DIR = "video_cache"
LOG_FILE = "logs/history.log"
ERROR_FILE = "logs/error.log"
CONFIG_FILE = "config.json"  # chưa dùng, để mở rộng caption tuỳ biến

# === Ghi log ===
def log(msg, error=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    with open(ERROR_FILE if error else LOG_FILE, "a") as f:
        f.write(line)
    print(line, end="")

# === Hàm chính ===
async def upload_video(filepath):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=".tiktok_profile",
            headless=False  # để nhìn thấy trình duyệt khi up
        )
        page = await browser.new_page()

        try:
            log(f"[UPLOADER] Đang mở TikTok studio")
            await page.goto("https://www.tiktok.com/upload", timeout=60000)

            # === Đợi nút upload xuất hiện ===
            input_elem = await page.wait_for_selector("input[type=file]", timeout=30000)
            await input_elem.set_input_files(filepath)
            log(f"[UPLOADER] Đã chọn file: {filepath}")

            # === Đợi caption tự sinh (TikTok auto fill title từ filename) ===
            await page.wait_for_timeout(5000)

            # === Ấn nút Đăng (Post) ===
            post_button = await page.wait_for_selector("button:has-text(Đăng)", timeout=30000)
            await post_button.click()
            log(f"[UPLOADER] ĐÃ ĐĂNG THÀNH CÔNG: {os.path.basename(filepath)}")

            await page.wait_for_timeout(10000)
            await browser.close()

        except Exception as e:
            log(f"[UPLOADER] ERROR – {e}", error=True)
            await browser.close()

# === Entry ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python uploader_tiktok.py <video_path>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Không tìm thấy file: {path}")
        sys.exit(1)

    asyncio.run(upload_video(path))
