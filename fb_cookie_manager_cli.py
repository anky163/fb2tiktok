import argparse
from fb_cookies_manager import is_cookie_expired, auto_renew_if_expired

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
parser.add_argument("--renew", action="store_true")
parser.add_argument("--cookie", type=str, default="fb_cookies.json")

args = parser.parse_args()

if args.check:
    expired = is_cookie_expired(args.cookie)
    print("✅ Cookie hợp lệ" if not expired else "❌ Cookie hết hạn")
elif args.renew:
    auto_renew_if_expired(args.cookie)
