# manual_upload.py

from playwright.sync_api import sync_playwright
import time

cookie_list = [
    {
        "name": "sid_tt",
        "value": "7dbf7537c4ae8afae239d785c7f90b06",
        "domain": ".tiktok.com",
        "path": "/",
        "httpOnly": True,
        "secure": True
    },
    {
        "name": "sessionid",
        "value": "7dbf7537c4ae8afae239d785c7f90b06",
        "domain": ".tiktok.com",
        "path": "/",
        "httpOnly": True,
        "secure": True
    },
    {
        "name": "tt_csrf_token",
        "value": "rFZK1uSV-AvUa3kFMnl9MBJkn-gn41pQKaFY",
        "domain": ".tiktok.com",
        "path": "/",
        "httpOnly": False,
        "secure": True
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Đưa cookie trước khi vô trang
    context.add_cookies(cookie_list)
    
    page.goto("https://www.tiktok.com/creator-center/upload")
    time.sleep(5)

    # Kiểm tra localStorage, hoặc reload để TikTok đọc cookie đúng
    page.reload()
    time.sleep(10)

    print("✅ Đã load trang upload, mày xem nút hiện chưa.")

    # Tạm dừng để mày can thiệp thủ công hoặc lấy selector nút
    input("Nhấn Enter để đóng...")

    browser.close()