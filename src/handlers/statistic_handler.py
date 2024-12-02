from datetime import datetime, timedelta
from pathlib import Path
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from handlers.supports.answer import STATISTIC_MESS, NO_CAMERA_EVENTS
from config import KITCHEN_ID, SCENARIO_ID
from handlers.supports.keyboards import get_back_keyboard
from services.kitchen_service import (
    get_people_disribution_on_kitchen_by_day,
)

router = Router()


@router.callback_query(lambda c: c.data == "statistics")
async def kitchen_statistics(
    callback_query: CallbackQuery, state: FSMContext
):
    path: Path | None = await get_people_disribution_on_kitchen_by_day(
        KITCHEN_ID,
        SCENARIO_ID,
        datetime.today() - timedelta(days=1),
        callback_query.message.from_user.id,
    )
    if path is None:
        await callback_query.message.answer(
            text=NO_CAMERA_EVENTS, reply_markup=await get_back_keyboard()
        )
    else:
        await callback_query.message.bot.send_photo(
            photo=FSInputFile(path),
            caption=STATISTIC_MESS,
            chat_id=callback_query.message.chat.id,
            reply_markup=await get_back_keyboard(),
        )
