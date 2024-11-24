from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


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


async def get_start_keyboard() -> ReplyKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Начать", callback_data="kitchen"
    )
    return keyboard_builder.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_kitchen_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Обновить", callback_data="update_kitchen_info"
    )
    keyboard_builder.button(
        text="Бронь", callback_data="booking"
    )
    keyboard_builder.button(
        text="Статистика", callback_data="kitchen_statistics"
    )
    return keyboard_builder.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Назад", callback_data="update_kitchen_info")
    return keyboard_builder.as_markup(one_time_keyboard=True, resize_keyboard=True)
