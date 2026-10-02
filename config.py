import os, sys

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    sys.exit("BOT_TOKEN is not set. Add it to your .env file.")
    
BOT_API_KEY = os.getenv("BOT_API_KEY", "")
if not BOT_API_KEY:
    raise RuntimeError("BOT_API_KEY is not set")

ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
if not ALLOWED_USER_ID:
    raise RuntimeError("ALLOWED_USER_ID is not set")

TRENDEN_URL = os.getenv("TRENDEN_URL", "").rstrip("/")
if not TRENDEN_URL:
    raise RuntimeError("TRENDEN_URL is not set")