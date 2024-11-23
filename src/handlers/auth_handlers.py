from json import load
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from services.auth_service import check_phone_number
from handlers.supports.state_machine import UserState
from handlers.supports.answer import (
    PHONE_NUMBER_EXISTS,
    PHONE_NUMBER_NOT_EXISTS,
)

router = Router()


@router.message(F.contact, UserState.phone_number)
async def get_user_password(message: types.Contact, state: FSMContext):
    phone_number = message.contact.phone_number
    if check_phone_number(phone_number):
        await state.update_data(phone_number=phone_number)
        await message.answer(text=PHONE_NUMBER_EXISTS)
    else:
        await message.answer(text=PHONE_NUMBER_NOT_EXISTS)
