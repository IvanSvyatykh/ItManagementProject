from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from handlers.supports.answer import (
    GREETING_MESS,
    PHONE_NUMBER_EXISTS,
    PHONE_NUMBER_NOT_EXISTS,
)
from handlers.supports.state_machine import UserState
from handlers.supports.keybords import get_phone_number_keyboard, get_start_keyboard
from services.auth_service import check_phone_number

router = Router()


@router.message(Command("start"))
async def start_dialog(message: types.Message, state: FSMContext):
    await message.answer(
        text=GREETING_MESS, reply_markup=await get_phone_number_keyboard()
    )
    await state.set_state(UserState.phone_number)


@router.message(F.contact, UserState.phone_number)
async def get_user_password(message: types.Contact, state: FSMContext):
    phone_number = message.contact.phone_number
    if check_phone_number(phone_number):
        await state.update_data(phone_number=phone_number)
        await message.answer(text=PHONE_NUMBER_EXISTS, reply_markup=await get_start_keyboard())
    else:
        await message.answer(text=PHONE_NUMBER_NOT_EXISTS)
        await state.update_data(phone_number=None)
