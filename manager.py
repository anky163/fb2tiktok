import subprocess
import time
import os

from config import DELAY_TIME

def load_pages(file_path="pages.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def start_stalkers(pages):
    procs = []
    for url in pages:
        page_name = url.strip('/').split('/')[-1]
        print(f"🚀 Cử stalker theo dõi: {page_name}")

        p = subprocess.Popen(["python", "stalker.py", url])
        procs.append((page_name, p))
        time.sleep(DELAY_TIME)  # delay nhẹ giữa các launch

    return procs

if __name__ == "__main__":
    pages = load_pages()

    if not pages:
        print("⚠️ Không tìm thấy fanpage nào trong pages.txt")
        exit(1)

    print(f"👥 Tổng cộng {len(pages)} fanpage. Bắt đầu rình...")

    procs = start_stalkers(pages)

    print("💤 Tất cả stalker đã được khởi chạy. Nhấn Ctrl+C để thoát.")
    try:
        for name, p in procs:
            p.wait()
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng tất cả stalker...")
        for _, p in procs:
            p.terminate()
