import time
import sys
import os
import asyncio
import re
import json
import subprocess
import aiohttp
from bs4 import BeautifulSoup
from pathlib import Path
from playwright.async_api import async_playwright

from fb_stalker.config import COOKIES_PATH, PROFILE_DIR, HISTORY_FILE, WAIT_BETWEEN_ROUNDS, STALKER_MOUSE_WHEEL

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
    subprocess.run(["python", "-m", script, url])

async def fetch_posts(session, page_id, limit=3):
    url = f"https://www.facebook.com/pages_reaction_units/more/?page_id={page_id}&cursor=&surface=www_pages_home&unit_count={limit}"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with session.get(url, headers=headers) as resp:
        return await resp.text()

async def run_stalker_async(page_url):
    seen_ids = load_video_history()

    # Step 1: Dùng Playwright để lấy page_id
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        print(f"🤫📸 Đang stalk: {page_url.strip('/').split('/')[-1]}")
        await page.goto(page_url, timeout=60000)

        html = await page.content()
        match = re.search(r'fb://page/(\d+)', html)
        if match:
            page_id = match.group(1)
            print(f"📌 Tìm được page_id: {page_id}")
        else:
            raise Exception("Không tìm được page ID từ HTML")

        await context.close()

    # Step 2: Dùng aiohttp để query backend Facebook
    async with aiohttp.ClientSession(cookies=load_cookies()) as session:
        html = await fetch_posts(session, page_id, limit=MAX_POSTS)
        soup = BeautifulSoup(html, "html.parser")
        links = [a['href'] for a in soup.find_all('a', href=True)]

        checked = 0
        for href in links:
            if '/videos/' in href or '/reel/' in href or '/watch/?v=' in href:
                full_url = normalize_href(href)
                vid = extract_video_id(full_url)
                if not vid:
                    continue
                if vid in seen_ids:
                    print(f"⏩ Video {vid} đã có trong lịch sử.")
                    continue

                if '/videos/' in href:
                    call_downloader('fb_stalker.fb_vid', full_url)
                else:
                    call_downloader('fb_stalker.fb_reel', full_url)

                seen_ids.add(vid)
                checked += 1
                if checked >= MAX_POSTS:
                    break

def load_cookies():
    with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    return {c['name']: c['value'] for c in cookies}

def run_stalker(page_url):
    asyncio.run(run_stalker_async(page_url))

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
        print(f"🛌 Ngủ {nap_time} phút rồi stalk fanpage: {fanpage} tiếp...")
        time.sleep(WAIT_BETWEEN_ROUNDS)
