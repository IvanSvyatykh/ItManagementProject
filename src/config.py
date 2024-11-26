import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")
WEB_HOOK_PATH = os.getenv("WEB_HOOK_PATH")
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DOMAIN = os.getenv("POSTGRES_DOMAIN")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
