from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def get_phone_number_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(
                text="Отправить номер телефона", request_contact=True
            )
        ]
    ]
    markup = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return markup
