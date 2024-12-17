from datetime import datetime, time, timedelta
from aiogram import Bot, types, Router, F
from config import BOT_TOKEN, SCENARIO_ID
from aiogram.types import (
    FSInputFile,
    CallbackQuery,
    InputMediaPhoto,
)
from aiogram.fsm.context import FSMContext
from handlers.utils.state_machine import UserState
from handlers.utils.keyboards import (
    get_main_keyboard,
    get_period_selection_keyboard,
    get_room_navigation_keyboard,
    get_pagination_keyboard,
)
from handlers.utils.answer import (
    NOT_ALLOWED_FUNC,
    SELECT_PERIOD_MESS,
    INPUT_PERIOD_MESS,
    BOOKING_STATUS_TEMPLATE,
)
from services.booking_read_service import (
    get_booking_status,
    get_events,
    split_message_into_pages,
)

router = Router()
ROOMS = [
    "Бла-Бла",
    "Зона отдыха 7 этаж",
    "Терочная",
    "Тет-а-тет",
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
    from_refresh = data.get("from_refresh", False)
    room_index = data.get("current_room_index", 0)
    room_name = ROOMS[room_index]

    room_status = await get_booking_status(room_name, SCENARIO_ID)
    booking_status = room_status["status"]
    next_booking_times = room_status["next_booking_time"]

    if next_booking_times is None:
        message_text = (
            f"📍 *{room_name}*\n\n"
            "🟢 На сегодня *нет брони*"
        )
    else:
        booked_intervals = "\n".join(
            f"       {event['start_time']} - {event['end_time']}"
            for event in next_booking_times
        )
        events_text = f"*Забронированные промежутки:*\n{booked_intervals}"
        current_status_text = f"{booking_status}"

        message_text = (
            f"📍 *{room_name}*\n\n"
            f"{current_status_text}\n\n"
            f"{events_text}"
        )

    if from_refresh:
        try:
            media = types.InputMediaPhoto(
                media=FSInputFile(room_status.get("photo_path", "")),
                caption=message_text,
                parse_mode="Markdown",
            )
            await bot.edit_message_media(
                chat_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                media=media,
                reply_markup=await get_room_navigation_keyboard(),
            )
        except Exception as e:
            print(f"Ошибка обновления сообщения: {e}")
    else:
        await callback_query.message.delete()
        await bot.send_photo(
            chat_id=callback_query.from_user.id,
            photo=FSInputFile(room_status.get("photo_path", "")),
            caption=message_text,
            parse_mode="Markdown",
            reply_markup=await get_room_navigation_keyboard(),
        )


@router.callback_query(lambda c: c.data.startswith("navigate_"))
async def select_room(callback_query: CallbackQuery, state: FSMContext):

    room_index = int(callback_query.data.split("_")[1])

    # Сохраняем индекс выбранной комнаты в состояние
    await state.update_data(from_refresh=True)
    await state.update_data(current_room_index=room_index)

    # Обновляем сообщение с информацией о выбранной комнате
    await update_booking_message(callback_query, state)


@router.callback_query(lambda c: c.data == "booking_list")
async def booking_list_handler(
        callback_query: CallbackQuery
):
    await callback_query.message.delete()
    await show_period_selection(callback_query)


async def show_period_selection(callback_query: CallbackQuery):
    message_text = "📅 Выберите период:"
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
    message = await callback_query.message.edit_text(
        text="✍🏻 Введите период в формате: *год-месяц-день год-месяц-день*",
        parse_mode="Markdown",
        reply_markup=await get_main_keyboard()
    )
    await state.update_data(messages_to_delete=[message.message_id])
    await state.set_state(UserState.waiting_for_period)


@router.message(F.text, UserState.waiting_for_period)
async def handle_period_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)
    try:
        start_date_str, end_date_str = message.text.split()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        events = await get_events(start_date, end_date)

        for msg_id in messages_to_delete:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception:
                pass

        await state.clear()

        if not events:
            await message.answer(
                f"📅 Список бронирования *{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}*:\n"
                f" Нет событий.",
                parse_mode="Markdown",
                reply_markup=await get_main_keyboard()
            )
        else:
            event_strings = [
                f"{event.get('location', 'Без указания')} — "
                f"{datetime.fromisoformat(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M')} - "
                f"{datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')}"
                for event in events
            ]
            header = f"📅 Список бронирования *{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}*:\n\n"
            pages = split_message_into_pages(header + "\n".join(event_strings))
            if len(pages) == 1:
                await message.answer(
                    pages[0],
                    parse_mode="Markdown",
                    reply_markup=await get_main_keyboard()
                )
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
        error_message = await message.answer(
            text="⚠️ *Неверно* введен период! ⚠️\n"
                 "✍🏻 Введите период в формате: *год-месяц-день год-месяц-день*",
            parse_mode="Markdown",
        )
        messages_to_delete.append(error_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)


async def send_events_message(
        callback_query: CallbackQuery,
        start_date: datetime,
        end_date: datetime,
        events: list,
):
    if not events:
        message_text = (
            f"📅 Список бронирования {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:\n"
            f" Нет событий."
        )
    else:
        message_text = f"📅 Список бронирования {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}:\n"
        event_strings = [
            f"{event.get('location', 'Без указания')} — "
            f"{datetime.fromisoformat(event['start']['dateTime']).strftime('%Y-%m-%d %H:%M')} - "
            f"{datetime.fromisoformat(event['end']['dateTime']).strftime('%H:%M')}"
            for event in events
        ]
        message_text += "\n".join(event_strings)

    await callback_query.message.edit_text(
        message_text,
        reply_markup=await get_main_keyboard()
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


@router.callback_query(lambda c: c.data == "update_booking_button")
async def update_booking_button(
        callback_query: CallbackQuery, state: FSMContext
):
    await state.update_data(from_refresh=True)
    await update_booking_message(callback_query, state)
