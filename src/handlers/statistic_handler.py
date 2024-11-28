from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from handlers.supports.answer import STATISTIC_MESS
from handlers.supports.keyboards import get_back_keyboard

router = Router()


@router.callback_query(lambda c: c.data == "statistics")
async def kitchen_statistics(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    message_id = user_data.get("message_id")
    await callback_query.message.bot.edit_message_media(
        media=types.InputMediaPhoto(
            media=FSInputFile("src/files/stat/stat_temp.png"),
            caption=STATISTIC_MESS
        ),
        chat_id=callback_query.message.chat.id,
        message_id=message_id,
        reply_markup=await get_back_keyboard(),
    )
