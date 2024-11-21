import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")
WEB_HOOK_PATH = os.getenv("WEB_HOOK_PATH")
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
