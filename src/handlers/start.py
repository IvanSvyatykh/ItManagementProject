from json import load
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

router = Router()

with open(r"src/handlers/answer.json", "r") as data_for_mess:
    mes_data = load(data_for_mess)


@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(text=mes_data["greeting_answer"])
