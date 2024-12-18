from datetime import datetime, timedelta
from pathlib import Path
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile
from database.db_core import AuthDBUnitOfWork
from handlers.utils.answer import STATISTIC_MESS, NO_CAMERA_EVENTS
from config import KITCHEN_ID, SCENARIO_ID
from handlers.utils.keyboards import get_back_keyboard
from services.statistics_service import (
    get_people_disribution_on_kitchen_by_day,
)

router = Router()


@router.callback_query(lambda c: c.data == "statistics")
async def kitchen_statistics(callback_query: CallbackQuery):
    uow = AuthDBUnitOfWork()
    with uow.start() as session:
        await session.stat_repository.insert(
            "stat_diagrams", datetime.now()
        )
    reply_markup = await get_back_keyboard()
    for i in range(1, 4):

        date = datetime.today() - timedelta(days=i)
        path: Path | None = await get_people_disribution_on_kitchen_by_day(
            KITCHEN_ID,
            SCENARIO_ID,
            date,
            callback_query.message.from_user.id,
        )
        reply_markup = await get_back_keyboard() if i == 3 else None
        if path is None:
            await callback_query.message.answer(
                text=NO_CAMERA_EVENTS.format(date.date()),
                reply_markup=reply_markup,
            )
        else:
            await callback_query.message.answer_photo(
                photo=FSInputFile(path),
                caption=STATISTIC_MESS.format(date.date()),
                reply_markup=reply_markup,
            )
