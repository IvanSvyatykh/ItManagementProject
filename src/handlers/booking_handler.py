from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from handlers.supports.answer import BOOKING_MESS
from handlers.supports.keybords import get_back_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "booking")
async def kitchen_booking(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    message_id = user_data.get("message_id")

    path = "src/files/kitchen_photo/kitchen_photo_temp.jpg"
    await callback_query.message.bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=FSInputFile("src/files/booking/Google_Calendar_icon.png"),
            caption=BOOKING_MESS
        ),
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        reply_markup=await get_back_keyboard(),
    )
