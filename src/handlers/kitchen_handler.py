from ast import Dict
from datetime import datetime
from pathlib import Path
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from config import BOT_TOKEN
from database.db_core import AuthDBUnitOfWork
from handlers.utils.answer import NOT_ALLOWED_FUNC, BAD_CODE
from config import KITCHEN_ID
from services.camera_events_service import get_last_camera_snapshot
from handlers.utils.keyboards import get_kitchen_keyboard

router = Router()


async def send_kitchen_info(chat_id: str, state: FSMContext) -> None:
    bot = Bot(token=BOT_TOKEN)
    uow = AuthDBUnitOfWork()
    with uow.start() as session:
        await session.stat_repository.insert(
            "kitchen_photo", datetime.now()
        )
    response: Dict[int, Path | None] = await get_last_camera_snapshot(
        KITCHEN_ID, chat_id
    )
    if response["status"] == 200:
        message = await bot.send_photo(
            chat_id=chat_id,
            photo=FSInputFile(response["path"]),
            reply_markup=await get_kitchen_keyboard(),
        )
        await state.update_data(message_id=message.message_id)
    else:
        await bot.send_message(
            chat_id=chat_id, text=BAD_CODE.format(response["status"])
        )


@router.callback_query(lambda c: c.data == "kitchen_info")
async def get_kitchen_info(
    callback_query: CallbackQuery, state: FSMContext
):
    user_data = await state.get_data()
    if (
        "phone_number" not in user_data
        or user_data["phone_number"] is None
    ):
        await callback_query.message.answer(text=NOT_ALLOWED_FUNC)
    else:
        await send_kitchen_info(
            callback_query.message.chat.id,
            state,
        )
