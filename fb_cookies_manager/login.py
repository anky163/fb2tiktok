import json
import asyncio
import os
from playwright.async_api import async_playwright

# === Đường dẫn ===
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COOKIE_FILE = os.path.join(ROOT_DIR, "fb_cookies.json")
CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")


# === Tự động login Facebook và lưu cookie nếu thành công ===
async def login_and_save_cookies():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Không tìm thấy {CONFIG_FILE}.")
        return False

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    fb_user = config.get("fb_user")
    fb_pass = config.get("fb_pass")

    if not fb_user or not fb_pass:
        print("❌ Thiếu fb_user hoặc fb_pass trong config.json")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🔐 Đang đăng nhập Facebook...")
        await page.goto("https://www.facebook.com/login")

        await page.fill('input[name="email"]', fb_user)
        await page.fill('input[name="pass"]', fb_pass)
        await page.click('button[name="login"]')

        # === Đợi cookie "c_user" xuất hiện, hoặc timeout sau 15s ===
        success = False
        for _ in range(30):
            cookies = await context.cookies("https://www.facebook.com")
            if any(c["name"] == "c_user" for c in cookies):
                success = True
                break
            await asyncio.sleep(0.5)

        if not success:
            print("❌ Login thất bại hoặc bị chặn, kiểm tra lại user/pass hoặc CAPTCHA.")
            await browser.close()
            return False

        # === Lưu cookies ===
        with open(COOKIE_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Login thành công. Cookie đã lưu: {COOKIE_FILE}")
        await browser.close()
        return True


def main():
    asyncio.run(login_and_save_cookies())


if __name__ == "__main__":
    main()
