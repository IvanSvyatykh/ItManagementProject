from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import CallbackQuery
from config import BOT_TOKEN
from handlers.supports.answer import (
    KITCHEN_PHOTO_CAPTURE,
    NOT_ALLOWED_FUNC,
)
from services.kitchen_service import get_people_on_kitchen
from handlers.supports.keybords import get_kitchen_keyboard

router = Router()


async def send_kitchen_info(
    chat_id: str, state: FSMContext, user_id: str
) -> None:
    bot = Bot(token=BOT_TOKEN)
    kitchen_info = await get_people_on_kitchen(22726, 255, user_id)
    message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(kitchen_info[1]),
        caption=KITCHEN_PHOTO_CAPTURE.format(kitchen_info[0]),
        reply_markup=await get_kitchen_keyboard(),
    )
    await state.update_data(message_id=message.message_id)


@router.callback_query(
    lambda c: c.data == "kitchen" or c.data == "update_kitchen_info"
)
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
            callback_query.message.from_user.id,
        )
