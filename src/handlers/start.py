from json import load
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.supports.answer import GREETING_MESS
from handlers.supports.state_machine import UserState
from handlers.supports.keybords import get_phone_number_keyboard

router = Router()


@router.message(Command("start"))
async def start_dialog(message: types.Message, state: FSMContext):
    await message.answer(
        text=GREETING_MESS, reply_markup=await get_phone_number_keyboard()
    )
    await state.set_state(UserState.phone_number)
