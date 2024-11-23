from aiogram import Bot, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN
from handlers.supports.answer import (
    KITCHEN_PHOTO_CAPTURE,
    NOT_ALLOWED_FUNC,
)
from services.kitchen_service import get_people_on_kitchen

router = Router()


@router.message(Command("kitchen"))
async def start_dialog(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data["phone_number"] is None:
        await message.answer(text=NOT_ALLOWED_FUNC)
    else:
        bot = Bot(token=BOT_TOKEN)
        kitchen_info = await get_people_on_kitchen()
        with open(kitchen_info[1], "rb") as photo_file:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_file,
                caption=KITCHEN_PHOTO_CAPTURE.format(kitchen_info[0]),
            )
