import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

from config import convert_json_to_netscape, COOKIES_PATH, PROFILE_DIR, STEALTH_SCRIPT

async def run():
    if not Path(PROFILE_DIR).exists():
        Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--start-maximized"
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        with open(STEALTH_SCRIPT, "r") as f:
            stealth_script = f.read()
        await page.add_script_tag(content=stealth_script)

        print("🌐 Đang mở Facebook...")
        await page.goto("https://www.facebook.com/login", timeout=60_000)

        print("🔐 Đăng nhập Facebook bằng tay...")
        await page.wait_for_url("https://www.facebook.com/", timeout=180_000)

        print("✅ Đăng nhập thành công. Đang lưu cookie...")
        cookies = await context.cookies()

        cookies_dir = Path(COOKIES_PATH).parent
        cookies_dir.mkdir(parents=True, exist_ok=True)

        existing_cookies = None
        if Path(COOKIES_PATH).exists():
            try:
                existing_cookies = json.load(open(COOKIES_PATH, 'r', encoding='utf-8'))
            except:
                existing_cookies = None

        if not cookies or cookies != existing_cookies:
            with open(COOKIES_PATH, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"💾 Cookie đã lưu: {COOKIES_PATH}")

            # 🆕 Convert sang Netscape sau khi lưu JSON
            convert_json_to_netscape(COOKIES_PATH)
        else:
            print(f"📜 Cookies đã tồn tại và không có thay đổi.")

        await asyncio.sleep(2)
        await context.close()

if __name__ == "__main__":
    asyncio.run(run())
