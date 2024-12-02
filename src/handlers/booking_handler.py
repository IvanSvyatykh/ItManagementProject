from datetime import datetime, time, timedelta
from aiogram import Bot, types, Router, F
from config import BOT_TOKEN, SCENARIO_ID
from aiogram.types import (
    FSInputFile,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from handlers.supports.state_machine import UserState
from handlers.supports.keyboards import (
    get_main_keyboard,
    get_period_selection_keyboard,
    get_room_navigation_keyboard,
    get_pagination_keyboard,
)
from handlers.supports.answer import (
    NOT_ALLOWED_FUNC,
    SELECT_PERIOD_MESS,
    INPUT_PERIOD_MESS,
    BOOKING_STATUS_TEMPLATE,
)
from services.booking_service import (
    get_booking_status,
    get_events,
    split_message_into_pages,
)

router = Router()
ROOMS = [
    "Тет-а-тет",
    "Бла-Бла",
    "Зона отдыха 7 этаж",
    "7 этаж у проектора",
    "Спортивная",
    "Терочная",
]


@router.callback_query(lambda c: c.data == "booking")
async def booking_handler(
    callback_query: CallbackQuery, state: FSMContext
):
    user_data = await state.get_data()
    if (
        "phone_number" not in user_data
        or user_data["phone_number"] is None
    ):
        await callback_query.message.answer(text=NOT_ALLOWED_FUNC)
    else:
        await state.update_data(current_room_index=0)
        await update_booking_message(callback_query, state)


@router.callback_query(lambda c: c.data == "update_booking")
async def update_booking_message(
    callback_query: CallbackQuery, state: FSMContext
):
    bot = Bot(token=BOT_TOKEN)
    data = await state.get_data()
    room_index = data.get("current_room_index", 0)
    room_name = ROOMS[room_index]

    # Получаем статус комнаты
    room_status = await get_booking_status(room_name, SCENARIO_ID)
    booking_status = room_status["status"]
    people_count = room_status["people_count"]
    next_booking_times = room_status["next_booking_time"]

    if next_booking_times:
        first_event = next_booking_times[0]
        events_text = f"{room_name} {first_event['start_time']} - {first_event['end_time']}\n"
        other_events = [
            f"{' ' * 30}{event['start_time']} - {event['end_time']}"
            for event in next_booking_times[1:]
        ]
        events_text += "\n".join(other_events)
    else:
        events_text = f"{room_name} На сегодня нет брони"

    # Формируем итоговый текст сообщения
    message_text = f"""{booking_status} [{people_count}] - {events_text}"""

    await bot.send_photo(
        chat_id=callback_query.from_user.id,
        photo=FSInputFile(room_status["photo_path"]),
        caption=message_text,
        reply_markup=await get_room_navigation_keyboard(),
    )


@router.callback_query(lambda c: c.data == "to_book")
async def to_book_handler(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()

    google_calendar_url = "https://calendar.google.com/"
    message_text = f"Перейдите по [ссылке]({google_calendar_url}), чтобы забронировать время."

    await callback_query.message.answer(
        text=message_text,
        reply_markup=await get_main_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data.startswith("navigate_"))
async def navigate_rooms(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("current_room_index", 0)
    direction = callback_query.data.split("_")[1]

    if direction == "left":
        new_index = (current_index - 1) % len(ROOMS)
    else:  # direction == "right"
        new_index = (current_index + 1) % len(ROOMS)

    await state.update_data(current_room_index=new_index)
    await update_booking_message(callback_query, state)


@router.callback_query(lambda c: c.data == "booking_list")
async def booking_list_handler(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.delete()
    await show_period_selection(callback_query)


async def show_period_selection(callback_query: CallbackQuery):
    message_text = "Выберите период:"
    await callback_query.message.answer(
        message_text, reply_markup=await get_period_selection_keyboard()
    )


@router.callback_query(lambda c: c.data == "period_today")
async def period_today_handler(callback_query: CallbackQuery):
    start_date = datetime.combine(datetime.today(), time.min)
    end_date = datetime.combine(datetime.today(), time.max)
    events = await get_events(start_date, end_date)
    await send_events_message(callback_query, start_date, end_date, events)


@router.callback_query(lambda c: c.data == "period_tomorrow")
async def period_tomorrow_handler(callback_query: CallbackQuery):
    tomorrow = datetime.today() + timedelta(days=1)
    start_date = datetime.combine(tomorrow, time.min)
    end_date = datetime.combine(tomorrow, time.max)
    events = await get_events(start_date, end_date)
    await send_events_message(callback_query, start_date, end_date, events)


@router.callback_query(lambda c: c.data == "period_week")
async def period_this_week_handler(callback_query: CallbackQuery):
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    events = await get_events(start_date, end_date)
    await send_events_message(callback_query, start_date, end_date, events)


@router.callback_query(lambda c: c.data == "period_input_period")
async def booking_choose_period_handler(
    callback_query: CallbackQuery, state: FSMContext
):
    message_text = (
        "Введите период в формате: год-месяц-день год-месяц-день"
    )
    await callback_query.message.edit_text(
        message_text, reply_markup=await get_main_keyboard()
    )
    await state.set_state(UserState.waiting_for_period)


@router.message(F.text, UserState.waiting_for_period)
async def handle_period_input(message: types.Message, state: FSMContext):
    try:
        start_date_str, end_date_str = message.text.split()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        events = await get_events(start_date, end_date)

        await state.clear()

        if not events:
            await message.answer(
                f"Список бронирования {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:\n"
                f" Нет событий."
            )
        else:
            event_strings = [
                f"{event.get('location', 'Без указания')} — "
                f"{datetime.fromisoformat(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M')} - "
                f"{datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')}"
                for event in events
            ]
            pages = split_message_into_pages("\n".join(event_strings))
            if len(pages) == 1:
                await message.answer(pages[0])
            else:
                current_page = 0
                await state.update_data(
                    pages=pages, current_page=current_page
                )
                await message.answer(
                    pages[current_page],
                    reply_markup=get_pagination_keyboard(
                        current_page, len(pages)
                    ),
                )
    except ValueError:
        await message.answer(
            "Неверно введен период! Введите период в формате: год-месяц-день год-месяц-день"
        )


async def send_events_message(
    callback_query: CallbackQuery,
    start_date: datetime,
    end_date: datetime,
    events: list,
):
    if not events:
        message_text = (
            f"Список бронирования {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:\n"
            f" Нет событий."
        )
    else:
        message_text = f"Список бронирования {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:\n"

        event_strings = [
            f"{event.get('location', 'Без указания')} — "
            f"{datetime.fromisoformat(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M')} - "
            f"{datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')}"
            for event in events
        ]
        message_text += "\n".join(event_strings)

    await callback_query.message.edit_text(
        message_text, reply_markup=await get_main_keyboard()
    )


@router.callback_query(lambda c: c.data.startswith("page_"))
async def handle_pagination(
    callback_query: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    pages = data.get("pages", [])
    current_page = int(callback_query.data.split("_")[1])

    await state.update_data(current_page=current_page)

    await callback_query.message.edit_text(
        pages[current_page],
        reply_markup=get_pagination_keyboard(current_page, len(pages)),
    )
