from calendar import monthrange
from datetime import datetime, timedelta

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
        text="Загруженность кухни", callback_data="statistics"
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
    """
    Генерирует клавиатуру для выбора переговорной комнаты.
    """
    keyboard_builder = InlineKeyboardBuilder()

    # Кнопка "Обновить"
    keyboard_builder.button(
        text="Обновить", callback_data="update_booking_button"
    )
    # Кнопки для выбора комнат
    keyboard_builder.button(text="Бла-Бла", callback_data="navigate_0")
    keyboard_builder.button(text="Зона отдыха 7эт.", callback_data="navigate_1")
    keyboard_builder.button(text="Тет-а-Тет", callback_data="navigate_3")
    keyboard_builder.button(text="Терочная", callback_data="navigate_2")

    # Нижние кнопки
    keyboard_builder.button(
        text="Список брони", callback_data="booking_list"
    )
    keyboard_builder.button(text="Забронировать", callback_data="to_book")
    keyboard_builder.button(text="Меню", callback_data="menu")

    # Устанавливаем нужное количество кнопок в строках
    return keyboard_builder.adjust(1, 2, 2, 2, 1).as_markup(resize_keyboard=True)


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


async def get_room_selection_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    rooms = [
        ("Бла-Бла", "room_BLA-BLA"),
        ("Зона отдыха 7эт.", "room_CHILL-ZONE-SEVEN"),
        ("Терочная", "room_TEROCHNAYA"),
        ("Тет-а-Тет", "room_TET-A-TET"),
    ]
    for room_name, callback in rooms:
        keyboard.button(text=room_name, callback_data=callback)
    keyboard.button(text="Назад", callback_data="update_booking")
    keyboard.button(text="Вернуться в Меню", callback_data="menu")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def get_calendar_keyboard(
        year: int = None, month: int = None
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    today = datetime.now()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    first_day_weekday, days_in_month = monthrange(year, month)

    # Отображение заголовка месяца и переключателей
    prev_month = 12 if month == 1 else month - 1
    next_month = 1 if month == 12 else month + 1
    prev_year = year - 1 if month == 1 else year
    next_year = year + 1 if month == 12 else year

    keyboard.row(
        InlineKeyboardButton(text="←", callback_data=f"change_month_{prev_year}_{prev_month:02d}"),
        InlineKeyboardButton(text=f"{month:02d}-{year}", callback_data="ignore"),
        InlineKeyboardButton(text="→", callback_data=f"change_month_{next_year}_{next_month:02d}"),
    )

    # Создание строк календаря
    week_row = []
    empty_days = first_day_weekday
    total_cells = (empty_days + days_in_month + 6) // 7 * 7

    for cell in range(total_cells):
        if cell < empty_days:
            week_row.append(InlineKeyboardButton(text="-", callback_data="ignore"))
        elif cell < empty_days + days_in_month:
            day = cell - empty_days + 1
            date_str = f"{year}{month:02d}{day:02d}"
            week_row.append(
                InlineKeyboardButton(text=f"{day:02d}", callback_data=f"date_{date_str}")
            )
        else:
            week_row.append(InlineKeyboardButton(text="-", callback_data="ignore"))

        if len(week_row) == 7:
            keyboard.row(*week_row)
            week_row = []

    keyboard.row(InlineKeyboardButton(text="Вернуться в Меню", callback_data="menu"))
    return keyboard.as_markup(resize_keyboard=True)


async def get_confirmation_date_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Да, продолжить бронирование", callback_data="confirm_date")
    keyboard.button(text="Нет, выбрать другую дату", callback_data="room_")
    keyboard.button(text="Вернуться в Меню", callback_data="menu")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def generate_time_keyboard(
        booked_slots
):
    time_slots = []
    current_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("17:30", "%H:%M")
    keyboard = InlineKeyboardBuilder()

    while current_time <= end_time:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)

    booked_slots_datetime = []
    for booked in booked_slots:
        booked_start = datetime.strptime(booked["start"], "%H:%M")
        booked_end = datetime.strptime(booked["end"], "%H:%M")
        booked_slots_datetime.append((booked_start, booked_end))

    # Для каждого промежутка времени создаем кнопку и проверяем, забронирован ли этот промежуток
    row = []
    for start_str in time_slots:
        start_time = datetime.strptime(start_str, "%H:%M")

        booked = False
        for booked_start, booked_end in booked_slots_datetime:
            if booked_start <= start_time < booked_end:
                booked = True
                break

        button_text = start_str if not booked else "-"
        callback_data = f"time_{start_str}" if not booked else "time_booked"

        row.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))

        if len(row) == 5:
            keyboard.row(*row)
            row = []

    if row:
        keyboard.row(*row)

    keyboard.row(InlineKeyboardButton(text="Ввести вручную", callback_data="manual_time_input"))
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data="update_booking"))
    keyboard.row(InlineKeyboardButton(text="Вернуться в Меню", callback_data="menu"))
    return keyboard.as_markup(resize_keyboard=True)


async def get_manual_input_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Отмена", callback_data="update_booking")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def generate_duration_keyboard(
        selected_datetime, free_slots
):
    keyboard = InlineKeyboardBuilder()

    for slot in free_slots:
        start = datetime.strptime(slot["start"], "%H:%M").replace(
            year=selected_datetime.year,
            month=selected_datetime.month,
            day=selected_datetime.day,
        )
        end = datetime.strptime(slot["end"], "%H:%M").replace(
            year=selected_datetime.year,
            month=selected_datetime.month,
            day=selected_datetime.day,
        )

        if start <= selected_datetime < end:
            max_duration = int((end - selected_datetime).total_seconds() // 60)  # Минуты

            # Создаем кнопки с интервалами в 30 минут
            for duration in range(30, max_duration + 1, 30):
                hours = duration // 60
                minutes = duration % 60
                button_text = f"{hours} ч. {minutes} м." if hours else f"{minutes} м."
                callback_data = f"duration_{duration}"

                keyboard.button(text=button_text, callback_data=callback_data)

    # Если нет доступных интервалов, добавляем кнопку с соответствующим сообщением
    if not keyboard.export():
        keyboard.button(text="Нет доступных интервалов", callback_data="ignore")

    keyboard.adjust(4)
    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data="update_booking"))
    keyboard.row(InlineKeyboardButton(text="Вернуться в меню", callback_data="menu"))
    return keyboard.as_markup(resize_keyboard=True)


async def get_summary_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Добавить", callback_data="add_summary")
    keyboard.button(text="Продолжить, без названия", callback_data="skip_summary")
    keyboard.button(text="Вернуться в меню", callback_data="menu")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def get_description_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Добавить", callback_data="add_description")
    keyboard.button(text="Продолжить, без описания", callback_data="skip_description")
    keyboard.button(text="Вернуться в меню", callback_data="menu")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


async def get_confirmation_booking_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Забронировать", callback_data="booking_confirmed")
    keyboard.button(text="Отменить", callback_data="update_booking")
    keyboard.button(text="Вернуться в меню", callback_data="menu")
    return keyboard.adjust(1).as_markup(resize_keyboard=True)
