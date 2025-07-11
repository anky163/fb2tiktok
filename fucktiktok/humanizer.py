"""
humanizer.py – Giả lập hành vi người dùng trong trình duyệt thực

📦 Chạy:
    python3 -m fucktiktok.humanizer --url URL1,URL2,... [--keep]

✅ Dùng Chrome thật (persistent context) tránh bị detect
✅ Mỗi domain lưu cookies riêng → cookies/<domain>_cookies.json
"""

import asyncio
import random
import argparse
import os, json
import aiohttp
from urllib.parse import unquote, urlparse
from datetime import datetime
from playwright.async_api import async_playwright
from fucktiktok.stealth import apply_stealth  # ✅


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE_DIR = os.path.join(BASE_DIR, "cookies")
USER_PROFILE = os.path.join(BASE_DIR, "chrome_profiles")


def get_domain_hint_from_url(url: str):
    host = urlparse(url).hostname or ""
    parts = host.split(".")
    return parts[-2] if len(parts) >= 2 else host

async def save_cookies(context):
    cookies = await context.cookies()
    if not cookies:
        print("❗Không có cookies để lưu.")
        return

    os.makedirs(COOKIE_DIR, exist_ok=True)
    by_domain = {}

    # Gom cookie theo domain gốc
    for c in cookies:
        dom = c["domain"].lstrip(".")
        parts = dom.split(".")
        if len(parts) < 2: continue
        domain_key = parts[-2]  # facebook.com → facebook
        by_domain.setdefault(domain_key, []).append(c)

    for domain_hint, cookie_list in by_domain.items():
        path = os.path.join(COOKIE_DIR, f"{domain_hint}_cookies.json")
        with open(path, "w") as f:
            json.dump(cookie_list, f, indent=2)
        print(f"✅ Lưu {len(cookie_list)} cookies → {path}")

# === Móc storage ===

async def save_storage(page):
    origin = page.url.split("/")[2].split(":")[0]
    domain = origin.split(".")[-2]  # facebook.com → facebook
    os.makedirs(COOKIE_DIR, exist_ok=True)

    local = await page.evaluate("JSON.stringify(localStorage)")
    with open(os.path.join(COOKIE_DIR, f"{domain}_local.json"), "w") as f:
        f.write(local)

    session = await page.evaluate("JSON.stringify(sessionStorage)")
    with open(os.path.join(COOKIE_DIR, f"{domain}_session.json"), "w") as f:
        f.write(session)

    print(f"💾 Đã lưu storage cho {domain} → cookies/{domain}_local.json")


async def load_cookies(context, domain_hint):
    path = os.path.join(COOKIE_DIR, f"{domain_hint}_cookies.json")
    if not os.path.exists(path):
        print(f"⚠️ Không tìm thấy cookie: {path}")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ Đã load {len(cookies)} cookies từ {path}")
    except Exception as e:
        print(f"❌ Lỗi load cookie: {e}")

# === Load storage để xem stories, videos nếu muốn ===
async def load_storage(page):
    origin = page.url.split("/")[2].split(":")[0]
    domain = origin.split(".")[-2]
    local_path = os.path.join(COOKIE_DIR, f"{domain}_local.json")
    session_path = os.path.join(COOKIE_DIR, f"{domain}_session.json")

    if os.path.exists(local_path):
        with open(local_path) as f:
            data = json.load(f)
        await page.evaluate("""(data) => {
            for (let k in data) localStorage.setItem(k, data[k]);
        }""", data)
        print(f"📦 Đã load localStorage → {domain}")

    if os.path.exists(session_path):
        with open(session_path) as f:
            data = json.load(f)
        await page.evaluate("""(data) => {
            for (let k in data) sessionStorage.setItem(k, data[k]);
        }""", data)
        print(f"📦 Đã load sessionStorage → {domain}")



async def behave_like_human(page):
    actions = [random_mouse_moves, scroll_randomly, random_hover_elements, idle_delay]
    selected = random.sample(actions, k=random.randint(2, len(actions)))
    for action in selected:
        try: await action(page)
        except: continue

async def random_mouse_moves(page):
    for _ in range(random.randint(3, 7)):
        x, y = random.randint(50, 800), random.randint(50, 600)
        await page.mouse.move(x, y, steps=random.randint(5, 20))
        await asyncio.sleep(random.uniform(0.2, 0.8))

async def scroll_randomly(page):
    for _ in range(random.randint(1, 3)):
        await page.mouse.wheel(0, random.randint(100, 600))
        await asyncio.sleep(random.uniform(0.5, 1.5))

async def random_hover_elements(page):
    elements = await page.query_selector_all("a, button, div")
    for _ in range(random.randint(1, 3)):
        if not elements: break
        el = random.choice(elements)
        try:
            box = await el.bounding_box()
            if box:
                await page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.3, 1.0))
        except: continue

async def idle_delay(page):
    await asyncio.sleep(random.uniform(1.5, 3.5))


# === Main ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Một hoặc nhiều URL, phân cách bằng dấu phẩy")
    parser.add_argument("--keep", action="store_true", help="Giữ trình duyệt sau khi chạy")
    args = parser.parse_args()

    urls = [u.strip() for u in args.url.split(",") if u.strip()]

    async def run():
        profile_dir = os.path.join(USER_PROFILE, "default")
        os.makedirs(profile_dir, exist_ok=True)

        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                profile_dir,
                headless=False,
                executable_path="/usr/bin/google-chrome",  # ✅ Chrome thật tại đây
                args=[
                    "--start-maximized",
                    "--force-device-scale-factor=1",
                    "--disable-blink-features=AutomationControlled"
                ]
            )

            for url in urls:
                domain_hint = get_domain_hint_from_url(url)

                # 👉 Load cookies trước khi mở tab
                await load_cookies(context, domain_hint)

                page = await context.new_page()
                await apply_stealth(page)
                await page.goto(url)

                # 👉 Inject storage sau khi page đã goto (bắt buộc)
                await load_storage(page)
                await page.reload()  # reload để FB nhận localStorage

                await asyncio.sleep(3)
                await behave_like_human(page)

                await save_cookies(context)

                try:
                    await page.wait_for_load_state("load", timeout=10_000)
                    await save_storage(page)
                except Exception as e:
                    print(f"⚠️ save_storage failed: {e}")

                if not args.keep:
                    await page.close()

            print("✅ Đã xử lý xong toàn bộ URL")

            if args.keep:
                print("🟢 Giữ trình duyệt mở. CTRL+C để thoát.")
                await asyncio.sleep(999999)
            else:
                await context.close()

    asyncio.run(run())
