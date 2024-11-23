from aiogram import Bot, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from config import BOT_TOKEN
from handlers.supports.answer import (
    KITCHEN_PHOTO_CAPTURE,
    NOT_ALLOWED_FUNC,
)
from services.kitchen_service import get_people_on_kitchen
from handlers.supports.keybords import get_kitchen_keyboard

router = Router()


async def send_kitchen_info(chat_id: str) -> None:
    bot = Bot(token=BOT_TOKEN)
    kitchen_info = await get_people_on_kitchen()
    await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(kitchen_info[1]),
        caption=KITCHEN_PHOTO_CAPTURE.format(kitchen_info[0]),
        reply_markup=await get_kitchen_keyboard(),
    )


@router.callback_query(lambda c: c.data == "update_kitchen_info")
async def update_kitchen_info(callback_query: types.CallbackQuery):
    await send_kitchen_info(callback_query.message.chat.id)


@router.message(Command("kitchen"))
async def get_kitchen_info(message: types.Message, state: FSMContext):
    user_data = await state.get_data()

    if (
        "phone_number" not in user_data
        or user_data["phone_number"] is None
    ):
        await message.answer(text=NOT_ALLOWED_FUNC)
    else:
        await send_kitchen_info(message.chat.id)
