from aiogram import Bot, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from config import BOT_TOKEN
from handlers.supports.answer import (
    KITCHEN_PHOTO_CAPTURE,
    NOT_ALLOWED_FUNC,
    STATISTIC_MESS,
    BOOKING_MESS,
)
from services.kitchen_service import get_people_on_kitchen
from handlers.supports.keybords import get_kitchen_keyboard

router = Router()


async def send_kitchen_info(chat_id: str, state: FSMContext) -> None:
    bot = Bot(token=BOT_TOKEN)
    kitchen_info = await get_people_on_kitchen()
    message = await bot.send_photo(
        chat_id=chat_id,
        photo=FSInputFile(kitchen_info[1]),
        caption=KITCHEN_PHOTO_CAPTURE.format(kitchen_info[0]),
        reply_markup=await get_kitchen_keyboard(),
    )
    await state.update_data(message_id=message.message_id)


@router.callback_query(lambda c: c.data == "update_kitchen_info")
async def update_kitchen_info(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    message_id = user_data.get("message_id")

    kitchen_info = await get_people_on_kitchen()
    await callback_query.message.bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=FSInputFile(kitchen_info[1]),
            caption=KITCHEN_PHOTO_CAPTURE.format(kitchen_info[0]),
        ),
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        reply_markup=await get_kitchen_keyboard(),
    )


@router.callback_query(lambda c: c.data == "kitchen")
async def get_kitchen_info(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    # Ну /kitchen и /kitchen_stat не существует... нужна ли тут вообще какая-то обработка
    if (
            "phone_number" not in user_data
            or user_data["phone_number"] is None
    ):
        await callback_query.message.answer(text=NOT_ALLOWED_FUNC)
    else:
        await send_kitchen_info(callback_query.message.chat.id, state)
