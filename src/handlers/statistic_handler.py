from pathlib import Path
from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from handlers.supports.answer import STATISTIC_MESS
from datetime import datetime, timedelta
from handlers.supports.keybords import get_back_keyboard
from services.kitchen_service import (
    get_people_disribution_on_kitchen_by_day,
)

router = Router()


@router.callback_query(lambda c: c.data == "statistics")
async def kitchen_statistics(
    callback_query: CallbackQuery, state: FSMContext
):
    user_data = await state.get_data()
    message_id = user_data.get("message_id")
    path: Path = await get_people_disribution_on_kitchen_by_day(
        22726,
        255,
        datetime.today() - timedelta(days=1),
        callback_query.message.from_user.id,
    )
    await callback_query.message.bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=FSInputFile(path),
            caption=STATISTIC_MESS,
        ),
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        reply_markup=await get_back_keyboard(),
    )
