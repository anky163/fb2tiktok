# login_tiktok_qr.py

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright

COOKIE_PATH = "cookies/tiktok_cookies.json"
PROFILE_DIR = "cookies/tiktok_qr_profile"

async def run():
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

        print("🌐 Đang mở TikTok...")
        await page.goto("https://www.tiktok.com/login", timeout=60_000)

        print("🔄 Đợi phần tử QR xuất hiện...")
        try:
            # Nút "Use QR Code" – cần bấm để hiện QR
            await page.wait_for_selector('text="Use QR code"', timeout=10_000)
            await page.click('text="Use QR code"')
        except:
            print("⚠️ Không thấy nút QR, có thể đã hiển thị sẵn")

        print("📱 Mở app TikTok, quét QR code trên màn hình")
        await page.wait_for_url("https://www.tiktok.com/*", timeout=180_000)

        print("✅ Đăng nhập thành công. Đang lưu cookie...")
        cookies = await context.cookies()
        Path(COOKIE_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIE_PATH, "w") as f:
            json.dump(cookies, f, indent=2)
        print(f"💾 Cookie đã lưu: {COOKIE_PATH}")

        await asyncio.sleep(2)
        await context.close()

if __name__ == "__main__":
    asyncio.run(run())
