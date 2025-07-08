# login_cookie.py

from playwright.sync_api import sync_playwright
import json

p = sync_playwright().start()

context = p.chromium.launch_persistent_context(
    user_data_dir="./tiktok_user_data",
    headless=False,
    args=["--start-maximized"]
)

page = context.new_page()
page.goto("https://www.tiktok.com/login")

input("⏳ Đăng nhập xong bấm Enter để lưu cookies...")

cookies = context.cookies()
with open("tiktok_cookies.json", "w") as f:
    json.dump(cookies, f, indent=2)

print("✅ Cookies saved. Browser sẽ giữ nguyên, tắt tay nếu muốn.")

# KHÔNG đóng context hay p — để user xài tiếp tab
