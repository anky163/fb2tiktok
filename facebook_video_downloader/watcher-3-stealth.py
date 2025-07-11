#!/usr/bin/env python3
import json
import time
import os
import re
from subprocess import run
from playwright.sync_api import sync_playwright

from facebook_video_downloader.utils import json_to_netscape, load_facebook_cookies, get_video_metadata
from facebook_video_downloader.fb_downloader import download_video

# ========= CONFIG =========
COOKIE_JSON = os.path.join("cookies/facebook_cookies.json")
TEMP_COOKIE_TXT = os.path.join("cookies_tmp.txt")
PAGES_FILE = os.path.join("pages.txt")
SCROLL_TIMES = 2
SCROLL_PAUSE = 2
WAIT_BETWEEN_PAGES = 2
WAIT_BETWEEN_ROUNDS = 5
DOWNLOADED = os.path.join("logs/downloaded.json")

# ========= HELPERS =========

def extract_video_ids(page):
    hrefs = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
    video_ids = set()
    for href in hrefs:
        m = re.search(r"/videos/(\d+)", href)
        if m:
            video_ids.add(m.group(1))
        else:
            m = re.search(r"[?&]v=(\d+)", href)
            if m:
                video_ids.add(m.group(1))
    return list(video_ids)

def fetch_recent_video_meta(page_url, page):
    print(f"[+] Truy cập: {page_url}videos")
    page.goto(page_url + "videos", timeout=60000)
    time.sleep(5)

    for _ in range(SCROLL_TIMES):
        page.mouse.wheel(0, 2)
        time.sleep(SCROLL_PAUSE)

    video_ids = extract_video_ids(page)
    print(f"\n🧲 Tìm thấy {len(video_ids)} video trong fanpage:")

    # Load downloaded.json để khỏi móc lại caption nếu đã tải rồi
    downloaded = {}
    if os.path.exists(DOWNLOADED):
        with open(DOWNLOADED, "r") as f:
            try:
                downloaded = json.load(f)
            except:
                print("⚠️ File downloaded.json lỗi, bỏ qua...")

    all_meta = []
    for vid in video_ids:
        meta = get_video_metadata(vid, cookie_file=TEMP_COOKIE_TXT)

        # In metadate để debug
        # print(f"[DEBUG] meta: {meta}")

        if meta and meta.get("upload_ts") and vid not in downloaded and meta["title"].strip() in ["Facebook", "Video"]:
            try:
                print(f"⚠️ Caption mờ ảo, tìm lại bằng Playwright cho {vid}...")
                url = f"https://www.facebook.com/watch/?v={vid}"
                page.goto(url, timeout=30000)
                time.sleep(2)
                elems = page.query_selector_all("div[dir=auto]")
                texts = [e.inner_text() for e in elems if e.inner_text().strip()]
                if texts:
                    meta["title"] = texts[0].strip()
            except Exception as e:
                print(f"⚠️ Lỗi khi tìm caption fallback: {e}")
            all_meta.append(meta)

    print(f"tìm thấy {len(all_meta)} video mới nhất để fetch")
    sorted_meta = sorted(all_meta, key=lambda m: m["upload_ts"], reverse=True)
    return sorted_meta[:10]

# ========= MAIN =========

def main():
    print(f"[+] Chuyển cookies từ {COOKIE_JSON} → {TEMP_COOKIE_TXT}")
    json_to_netscape(COOKIE_JSON, TEMP_COOKIE_TXT)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="chrome_profiles/facebook",
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        # Inject stealth patch nếu có
        stealth_path = os.path.join("fucktiktok/stealth_patch-2.js")
        if os.path.exists(stealth_path):
            with open(stealth_path, "r") as f:
                stealth_script = f.read()
            page.add_init_script(stealth_script)
            print("🕵️ Injected stealth_patch-2.js")

        if not os.path.exists("chrome_profiles/facebook/first_cookie_done.flag"):
            page.goto("https://facebook.com", timeout=60000)
            page.context.add_cookies(load_facebook_cookies(COOKIE_JSON))
            with open("chrome_profiles/facebook/first_cookie_done.flag", "w") as f:
                f.write("ok")

        while True:
            with open(PAGES_FILE, "r") as f:
                pages = [line.strip() for line in f if line.strip() and "facebook.com" in line]

            for page_url in pages:
                try:
                    top10_meta = fetch_recent_video_meta(page_url, page)
                    print(f"\n🎯 Bắt đầu tải {len(top10_meta)} video mới nhất từ {page_url}:")
                    for meta in top10_meta:
                        url = f"https://www.facebook.com/watch/?v={meta['video_id']}"
                        download_video(url, metadata=meta)
                    time.sleep(WAIT_BETWEEN_PAGES)
                except Exception as e:
                    print(f"❌ Lỗi khi xử lý {page_url}: {e}")

            print(f"\n🔁 Đợi {WAIT_BETWEEN_ROUNDS}s rồi lặp lại từ đầu...")
            time.sleep(WAIT_BETWEEN_ROUNDS)

        browser.close()

if __name__ == "__main__":
    main()
