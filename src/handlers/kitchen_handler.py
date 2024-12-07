from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
from config import BOT_TOKEN
from handlers.utils.answer import (
    KITCHEN_PHOTO_CAPTURE,
    NOT_ALLOWED_FUNC,
)
from config import KITCHEN_ID, SCENARIO_ID
from services.camera_events_service import get_last_camera_event
from handlers.utils.keyboards import get_kitchen_keyboard

router = Router()


async def send_kitchen_info(chat_id: str, state: FSMContext) -> None:
    bot = Bot(token=BOT_TOKEN)
    kitchen_info = await get_last_camera_event(KITCHEN_ID)
    if kitchen_info["meta"] is None:
        caption = KITCHEN_PHOTO_CAPTURE.format(kitchen_info["people_nums"])
    else:
        caption = KITCHEN_PHOTO_CAPTURE.format(
            kitchen_info["people_nums"], kitchen_info["meta"]
        )
    message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(kitchen_info["path_to_photo"]),
        caption=caption,
        reply_markup=await get_kitchen_keyboard(),
    )
    await state.update_data(message_id=message.message_id)


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
