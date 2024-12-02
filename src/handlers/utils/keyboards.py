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
        text="Информация о кухне", callback_data="kitchen_info"
    )
    keyboard_builder.button(
        text="Бронирование переговорных", callback_data="booking"
    )
    keyboard_builder.button(
        text="Гистограмма загруженности кухни", callback_data="statistics"
    )
    return keyboard_builder.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_kitchen_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Обновить", callback_data="kitchen_info")
    keyboard_builder.button(text="Назад", callback_data="menu")
    return keyboard_builder.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Назад", callback_data="menu")
    return keyboard_builder.as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_room_navigation_keyboard() -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(
        text="Обновить", callback_data="update_booking"
    )
    keyboard_builder.button(text="←", callback_data="navigate_left")
    keyboard_builder.button(text="→", callback_data="navigate_right")
    keyboard_builder.button(
        text="Список брони", callback_data="booking_list"
    )
    keyboard_builder.button(text="Забронировать", callback_data="to_book")
    keyboard_builder.button(text="Меню", callback_data="menu")

    return keyboard_builder.adjust(1, 2, 2, 1).as_markup(
        resize_keyboard=True
    )


async def get_period_selection_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="За сегодня", callback_data="period_today")
    keyboard.button(text="На завтра", callback_data="period_tomorrow")
    keyboard.button(text="На эту неделю", callback_data="period_week")
    keyboard.button(
        text="Ввести вручную", callback_data="period_input_period"
    )
    keyboard.button(text="Назад", callback_data="update_booking")
    return keyboard.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


async def get_main_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Назад", callback_data="update_booking")
    return keyboard.adjust(1).as_markup(
        one_time_keyboard=True, resize_keyboard=True
    )


def get_pagination_keyboard(
    current_page: int, total_pages: int
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    if current_page == 0:  # Первая страница
        keyboard.button(text="✖", callback_data="close")
        keyboard.button(text="→", callback_data=f"page_{current_page + 1}")
    elif 0 < current_page < total_pages - 1:  # Промежуточные страницы
        keyboard.button(text="←", callback_data=f"page_{current_page - 1}")
        keyboard.button(text="→", callback_data=f"page_{current_page + 1}")
    elif current_page == total_pages - 1:  # Последняя страница
        keyboard.button(text="←", callback_data=f"page_{current_page - 1}")
        keyboard.button(text="✖", callback_data="close")
    keyboard.button(text="Назад", callback_data="update_booking")
    return keyboard.adjust(2).as_markup(resize_keyboard=True)
