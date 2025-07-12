import time
import sys
import os
import re
import json
import subprocess
from pathlib import Path
from time import sleep
from playwright.sync_api import sync_playwright

from config import PROFILE_DIR, HISTORY_FILE, WAIT_BETWEEN_ROUNDS

MAX_POSTS = 3

def normalize_href(href: str) -> str:
    href = href.split('?')[0]
    return href if href.startswith("http") else f"https://www.facebook.com{href}"

def load_video_history():
    if Path(HISTORY_FILE).exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return {item['video_id'] for item in json.load(f)}
        except:
            return set()
    return set()

def extract_video_id(url: str) -> str | None:
    match = re.search(r'(?:videos|reel|watch/\?v=)[^\d]*(\d{5,})', url)
    return match.group(1) if match else None

def call_downloader(script: str, url: str):
    # print(f"▶️ Gọi {script} {url}")
    subprocess.run(["python", script, url])

def run_stalker(page_url):
    seen_ids = load_video_history()
    # print(f"📜 Đã có {len(seen_ids)} videos trong lịch sử.")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print(f"🌐 Đang stalk: {page_url.strip('/').split('/')[-1]}")
        page.goto(page_url, timeout=60000)
        page.wait_for_selector('div[role="article"]', timeout=15000)

        # print("🖱️ Scroll nhẹ để load thêm post")
        page.mouse.wheel(0, 1500)
        sleep(3)

        posts = page.locator('div[role="article"]')
        total = posts.count()
        # print(f"🧩 Tổng số post detect được: {total}")

        checked = 0
        for i in range(min(MAX_POSTS, total)):
            post = posts.nth(i)
            html = post.inner_html()
            hrefs = re.findall(r'href="([^"]+)"', html)

            for href in hrefs:
                """
                # Yell nếu phát hiện có post là video hoặc reel
                if any(p in href for p in ["/videos/", "/reel/", "/watch/?v="]):
                    print(f"🔗🔗🔗🔗🔗 [DEBUG] Detected media href: {href}")
                """
                
                if '/videos/' in href:
                    full_url = normalize_href(href)
                    vid = extract_video_id(full_url)
                    if vid and vid not in seen_ids:
                        call_downloader("fb_vid.py", full_url)
                        seen_ids.add(vid)
                    else:
                        print(f"⏩ Video {vid} đã có trong lịch sử.")
                    break
                elif '/reel/' in href or '/watch/?v=' in href:
                    full_url = normalize_href(href)
                    vid = extract_video_id(full_url)
                    if vid and vid not in seen_ids:
                        call_downloader("fb_reel.py", full_url)
                        seen_ids.add(vid)
                    else:
                        print(f"⏩ Reel {vid} đã có trong lịch sử.")
                    break

            checked += 1
            if checked >= MAX_POSTS:
                break

        context.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("⚠️ Usage: python stalker.py <facebook_fanpage_url>")
        sys.exit(1)

    url = sys.argv[1]

    while True:
        try:
            run_stalker(url)
        except Exception as e:
            print(f"❌ Lỗi trong vòng stalk: {e}")

        nap_time = int(WAIT_BETWEEN_ROUNDS / 60)
        fanpage = url.strip('/').split('/')[-1]
        print(f"😴 Ngủ {nap_time} phút rồi stalk fanpage: {fanpage} tiếp...")
        time.sleep(WAIT_BETWEEN_ROUNDS)  # nghỉ N phút