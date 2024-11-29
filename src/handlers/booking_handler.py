from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from handlers.supports.answer import BOOKING_MESS
from handlers.supports.keybords import get_back_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "booking")
async def kitchen_booking(
    callback_query: CallbackQuery, state: FSMContext
):
    user_data = await state.get_data()
    message_id = user_data.get("message_id")

    await callback_query.message.bot.edit_message_media(
        media=InputMediaPhoto(
            media=FSInputFile(
                "src/files/booking/Google_Calendar_icon.png"
            ),
            caption=BOOKING_MESS,
        ),
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        reply_markup=await get_back_keyboard(),
    )
