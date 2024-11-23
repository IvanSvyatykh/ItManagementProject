import asyncio
import datetime
from logging import basicConfig, INFO, FileHandler, StreamHandler
from pathlib import Path
import time
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, WEB_HOOK_URL, WEB_HOOK_PATH, WEB_SERVER_HOST
from aiohttp import web
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from handlers import start, auth_handlers


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{WEB_HOOK_URL}{WEB_HOOK_PATH}")


async def set_up_logger(path_to_log_file: Path):
    if not path_to_log_file.exists():
        path_to_log_file.touch(exist_ok=True)

    with open(path_to_log_file, "w") as f:
        f.write(
            f"Bot has started at {datetime.datetime.now().astimezone()}"
        )

    basicConfig(
        level=INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        handlers=[
            FileHandler(path_to_log_file),
            StreamHandler(),
        ],
    )


async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(auth_handlers.router)
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    await set_up_logger(Path("src/logs/bot_logs.log"))
    webhook_requests_handler.register(app, path=WEB_HOOK_PATH)
    setup_application(app, dp, bot=bot)
    await web._run_app(app, host=WEB_SERVER_HOST)


if __name__ == "__main__":
    asyncio.run(main())
