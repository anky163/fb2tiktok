# tiktok_uploader/uploader.py

import asyncio
import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from tiktok_uploader.utils import load_cookies, print_log

# ======== Config ===========================================

VIDEO_DIR = os.path.join("video_cache/")
DOWNLOADED_JSON = os.path.join("logs/downloaded.json")
UPLOADED_JSON = os.path.join("logs/uploaded.json")
STEALTH_PATCH = os.path.join("fucktiktok/stealth_patch-2.js")

# ===========================================================

async def upload_video(page, video_path, caption):
    print_log(f"Đang upload: {video_path}")
    await page.goto("https://www.tiktok.com/tiktokstudio/upload?lang=en", timeout=60_000)

    # Scroll sớm để kích hoạt lazy-load input[type=file]
    await page.evaluate("window.scrollBy(0, 500)")
    await page.wait_for_timeout(1000)

    # Click nút "Chọn video" để TikTok render input[type=file]
    try:
        await page.click('button[data-e2e="select_video_button"]', timeout=10000)
        print_log("🟢 Clicked select_video_button")
        await page.wait_for_timeout(1000)
    except:
        print_log("⚠️ Không tìm thấy nút chọn video")

    # Đợi input[type=file] xuất hiện thật sự
    inputs = await page.eval_on_selector_all("input", "els => els.map(e => e.outerHTML)")
    print_log(f"[DEBUG] Found {len(inputs)} input(s)")
    for i, el in enumerate(inputs):
        print_log(f"[DEBUG] input[{i}]: {el[:100]}...")

    # Bỏ ẩn input[type=file] nếu cần
    await page.evaluate("""() => {
        const input = document.querySelector('input[type=file]');
        if (input) {
            input.removeAttribute('hidden');
            input.style.display = 'block';
        }
    }""")

    await page.wait_for_selector("input[type='file'][accept='video/*']", state="attached", timeout=60000)
    print_log("🟢 input[type='file'][accept='video/*'] found")
    print_log("🟢 input[type=file] ready")

    await page.set_input_files("input[type=file]", video_path)
    await page.wait_for_timeout(5000)  # Tăng delay để TikTok xử lý video

    # Debug xem thumbnail overlay có load không
    try:
        await page.wait_for_selector("div.video-overlay-container div", timeout=15000)
        print_log("🟢 Thumbnail overlay loaded")
    except:
        print_log("⚠️ Thumbnail overlay không xuất hiện (TikTok chưa xử lý xong video?)")

    # Chờ thêm để đảm bảo thumbnail không còn "Loading..."
    try:
        await page.wait_for_function("""
            () => {
                const el = document.querySelector(".video-overlay-container div");
                return el && el.innerText.trim() !== "Loading...";
            }
        """, timeout=30_000)
        print_log("🟢 Thumbnail ready (Loading... cleared)")
    except:
        print_log("⚠️ Thumbnail vẫn chưa ready. Có thể video lỗi hoặc TikTok đang chậm.")
        return False

    # Scroll nhẹ để hiện phần nhập caption
    await page.evaluate("window.scrollBy(0, 300)")
    await page.wait_for_timeout(1000)

    # Đợi caption editor hiển thị đúng vùng contenteditable
    await page.wait_for_selector('[contenteditable="true"]', timeout=60_000)
    print_log("🟢 contenteditable found")

    # Điền caption bằng eval để xử lý contenteditable phức tạp
    await page.evaluate(f"""
        (caption) => {{
            const el = document.querySelector('[contenteditable="true"]');
            if (el) {{
                el.focus();
                const range = document.createRange();
                range.selectNodeContents(el);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('insertText', false, caption);
            }}
        }}
    """, caption)
    await page.wait_for_timeout(1000)

    # Đợi đến khi nút Post thực sự khả dụng
    await page.wait_for_selector('button[data-e2e="post_video_button"][aria-disabled="false"]', timeout=180_000)
    print_log("🟢 post_video_button is enabled")
    await page.click('button[data-e2e="post_video_button"]')
    print_log("Đã bấm Post. TikTok sẽ xử lý ngầm.")
    await page.wait_for_timeout(3000)  # Cho TikTok phản hồi lỗi (nếu có)

    # Check xem có lỗi hiển thị không sau khi bấm Post
    error_divs = await page.query_selector_all("div:has-text('đã xảy ra lỗi')")
    if error_divs:
        print_log("❌ TikTok báo lỗi ngay sau khi bấm Post.")
        """
        for i, err in enumerate(error_divs):
            msg = await err.inner_text()
            html = await err.evaluate("el => el.outerHTML")
            box = await err.bounding_box()

            print_log(f"[TikTokError-{i}] {msg}")
            print_log(f"[TikTokError-{i} HTML] {html[:300]}...")
            print_log(f"[TikTokError-{i} BBox] {box}")
        """
        return False


    print_log("✅ Upload *đang* diễn ra, không chờ hoàn tất.")
    return True

async def run():
    # Load metadata
    downloaded = json.load(open(DOWNLOADED_JSON)) if Path(DOWNLOADED_JSON).exists() else {}
    uploaded = json.load(open(UPLOADED_JSON)) if Path(UPLOADED_JSON).exists() else {}

    videos = [f for f in os.listdir(VIDEO_DIR) if re.match(r"_v_\d+\.mp4", f)]
    if not videos:
        print_log("Không có video nào để upload")
        return

    cookies = load_cookies()

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="cookies/tiktok_uploader_profile",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--remote-debugging-port=9222"
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Inject stealth nếu có
        if os.path.exists(STEALTH_PATCH):
            with open(STEALTH_PATCH, "r") as f:
                await page.add_init_script(f.read())
            print_log("🕵️ Injected stealth_patch-2.js")

        # Set cookies (nếu chưa login sẵn)
        await context.add_cookies(cookies)
        await page.goto("https://www.tiktok.com/", timeout=60_000)

        if "login" in page.url:
            print_log("⚠️ Cookie hết hạn hoặc TikTok bắt login lại. Dừng.")
            return

        for filename in videos:
            match = re.match(r"_v_(\d+)\.mp4", filename)
            if not match:
                continue
            vid = match.group(1)
            if vid in uploaded:
                print_log(f"Đã upload trước đó: {vid}, bỏ qua")
                continue

            meta = downloaded.get(vid, {})
            caption = meta["caption"]
            ts = meta.get("timestamp", 0)

            try:
                success = await upload_video(page, os.path.join(VIDEO_DIR, filename), caption)
                print_log(f"[DEBUG] upload_video returned: {success}")

                if success:
                    # Xoá file sau khi thành công
                    os.remove(os.path.join(VIDEO_DIR, filename))

                    # Ghi log upload
                    uploaded[vid] = {
                        "caption": caption,
                        "timestamp": ts,
                        "uploaded_at": int(time.time())
                    }
                    with open(UPLOADED_JSON, "w") as f:
                        json.dump(uploaded, f, indent=2)

            except Exception as e:
                print_log(f"❌ Lỗi khi upload {vid}: {e}")

        print_log("🛑 Giữ trình duyệt mở để quan sát upload. Nhấn Ctrl+C để thoát.")
        while True:
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run())
