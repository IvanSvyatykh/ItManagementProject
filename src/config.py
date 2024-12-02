import ast
import os
from dotenv import load_dotenv

load_dotenv()
# Bot envs
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_HOOK_URL = os.getenv("WEB_HOOK_URL")
WEB_HOOK_PATH = os.getenv("WEB_HOOK_PATH")
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST")
# IS camera events db
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DOMAIN = os.getenv("POSTGRES_DOMAIN")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
# Google calendar API
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = ast.literal_eval(os.getenv("SCOPES"))
CALENDAR_ID = os.getenv("CALENDAR_ID")
# auth db
AUTH_DB_NAME = os.getenv("AUTH_DB_NAME")
AUTH_DB_USER = os.getenv("AUTH_DB_USER")
AUTH_DB_PASSWORD = os.getenv("AUTH_DB_PASSWORD")
AUTH_DB_PORT = os.getenv("AUTH_DB_PORT")
AUTH_DB_DOMAIN = os.getenv("AUTH_DB_DOMAIN")
