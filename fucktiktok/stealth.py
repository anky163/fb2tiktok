# stealth.py – Stealth deep: Canvas, WebGL, Audio, Iframe traps

import os

async def apply_stealth(page):
    js_path = os.path.join(os.path.dirname(__file__), "stealth_patch-2.js")
    await page.context.add_init_script(path=js_path)
