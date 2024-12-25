import asyncio
from datetime import datetime, timedelta, time
import random
import pytz
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, User
from aiogram.fsm.context import FSMContext
from handlers.utils.keyboards import (
    get_room_selection_keyboard,
    get_calendar_keyboard,
    get_confirmation_date_keyboard,
    get_main_keyboard,
    generate_time_keyboard,
    get_manual_input_keyboard,
    generate_duration_keyboard,
    get_description_keyboard,
    get_confirmation_booking_keyboard,
    get_summary_keyboard,
)
from services.booking_write_service import (
    create_google_calendar_event,
)
from services.booking_read_service import (
    get_booked_slots_for_room,
    get_free_slots,
    normalize_location,
    get_events,
)
from handlers.utils.state_machine import BookingStates

router = Router()
TIMEZONE = pytz.timezone("Asia/Yekaterinburg")


@router.callback_query(lambda c: c.data == "to_book")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        text="*Выберите* переговорную:",
        parse_mode="Markdown",
        reply_markup=await get_room_selection_keyboard(),
    )


@router.callback_query(lambda c: c.data.startswith("room_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split("_")
    room_id = data_parts[1] if len(data_parts) > 1 and data_parts[1] else None
    print(room_id)
    if not room_id:
        data = await state.get_data()
        room_id = data.get("selected_room")
        if not room_id:
            await callback.message.edit_text(
                text="⚠️ *Ошибка* при выборе _переговорной_. Попробуйте позже. ⚠️",
                parse_mode="Markdown",
                reply_markup=await get_main_keyboard(),
            )
            return

    await state.update_data(selected_room=room_id)
    await callback.message.edit_text(
        text="🗓 *Выберите* дату бронирования 🗓",
        parse_mode="Markdown",
        reply_markup=await get_calendar_keyboard(),
    )
    await state.set_state(BookingStates.SELECT_DATE)


@router.callback_query(lambda c: c.data == "confirm_date", BookingStates.CONFIRM_DATE)
async def confirm_date(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    booked_slots_text = data.get("booked_slots_text")
    booked_slots = data.get("booked_slots")
    free_slots_text = data.get("free_slots_text")
    await callback.message.edit_text(
        text=f"📍 *{selected_room} - {selected_date}*  📅\n\n"
             f"❌ *Забронированные* промежутки времени:\n"
             f"        {booked_slots_text.replace('\n', '\n        ')}\n"
             f"✅ *Свободные* промежутки времени:\n"
             f"        {free_slots_text.replace('\n', '\n        ')}\n\n"
             "🕓 Выберите *время начала* бронирования:",
        reply_markup=await generate_time_keyboard(booked_slots),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data.startswith("change_month_"))
async def change_month(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        _, _, year, month = parts
        year = int(year)
        month = int(month)

        if not (1 <= month <= 12):
            raise ValueError("Month is out of range")

        await callback.message.edit_text(
            text="🗓 Выберите дату:",
            reply_markup=await get_calendar_keyboard(year=year, month=month),
        )
    except ValueError as e:
        print(f"Error in change_month handler: {e}")
        await callback.message.answer(
            text="⚠️ Произошла *ошибка* при обработке выбора месяца. Попробуйте позже. ⚠️",
            parse_mode="Markdown",
        )


@router.callback_query(lambda c: c.data.startswith("date_"), BookingStates.SELECT_DATE)
async def handle_date_selection(
        callback: CallbackQuery, state: FSMContext
):
    date = callback.data.split("_")[1]
    selected_date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    selected_datetime = datetime.strptime(date, "%Y%m%d")
    selected_weekday = selected_datetime.weekday()

    data = await state.get_data()
    selected_room = await normalize_location(data.get("selected_room", "Бла-Бла"))
    await state.update_data(selected_room=selected_room)
    booked_slots = await get_booked_slots_for_room(
        room_name=selected_room,
        start_date=selected_datetime.replace(hour=8, minute=0, second=0),
        end_date=selected_datetime.replace(hour=18, minute=0, second=0)
    )

    free_slots = get_free_slots(booked_slots, selected_datetime.replace(hour=8, minute=0, second=0),
                                selected_datetime.replace(hour=18, minute=0, second=0))

    if not booked_slots:
        booked_slots_text = "Не забронировано"
    else:
        booked_slots_text = "\n".join([f"{slot['start']} - {slot['end']}" for slot in booked_slots])
    free_slots_text = "\n".join([f"{slot['start']} - {slot['end']}" for slot in free_slots])

    await state.update_data(booked_slots=booked_slots)
    await state.update_data(free_slots=free_slots)
    await state.update_data(booked_slots_text=booked_slots_text)
    await state.update_data(free_slots_text=free_slots_text)

    # Проверка на прошедшую дату
    if selected_datetime.date() < datetime.now().date():
        await state.update_data(selected_date=selected_date)
        await callback.message.edit_text(
            text=f"❕ Выбранная дата _{selected_date}_ *уже прошла*. ❕\n"
                 f"Вы уверены, что хотите забронировать на этот день?",
            parse_mode="Markdown",
            reply_markup=await get_confirmation_date_keyboard(),
        )
        await state.set_state(BookingStates.CONFIRM_DATE)
    # Проверка на выходной день
    elif selected_weekday >= 5:
        await state.update_data(selected_date=selected_date)
        await callback.message.edit_text(
            text=f"❕ Выбранная дата _{selected_date}_ - *выходной день*. ❕\n"
                 "Вы уверены, что хотите забронировать на этот день?",
            parse_mode="Markdown",
            reply_markup=await get_confirmation_date_keyboard(),
        )
        await state.set_state(BookingStates.CONFIRM_DATE)
    else:
        await state.update_data(selected_date=selected_date)

        await callback.message.edit_text(
            text=f"📍 *{selected_room} - {selected_date}*  📅\n\n"
                 f"❌ *Забронированные* промежутки времени:\n"
                 f"        {booked_slots_text.replace('\n', '\n        ')}\n"
                 f"✅ *Свободные* промежутки времени:\n"
                 f"        {free_slots_text.replace('\n', '\n        ')}\n\n"
                 "🕓 Выберите *время начала* бронирования:",
            reply_markup=await generate_time_keyboard(booked_slots),
            parse_mode="Markdown",
        )


@router.callback_query(lambda c: c.data == "manual_time_input")
async def handle_manual_time_input(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    booked_slots_text = data.get("booked_slots_text")
    free_slots_text = data.get("free_slots_text")

    prompt_message = await callback.message.edit_text(
        text=f"📍 *{selected_room} - {selected_date}*  📅\n\n"
             f"❌ *Забронированные* промежутки времени:\n"
             f"        {booked_slots_text.replace('\n', '\n        ')}\n\n"
             f"✅ *Свободные* промежутки времени:\n"
             f"        {free_slots_text.replace('\n', '\n        ')}\n\n"
             "✍🏻 Введите время бронирования в формате *ч м ч м*\n"
             "Например _11 00 12 00_",
        reply_markup=await get_manual_input_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(BookingStates.INPUT_TIME)
    # Сохраняем ID сообщения для его удаления
    await state.update_data(prompt_message_id=prompt_message.message_id)


@router.message(F.text, BookingStates.INPUT_TIME)
async def handle_period_input(
        message: types.Message, state: FSMContext
):
    user_input = message.text.strip()
    data = await state.get_data()
    booked_slots = data.get("booked_slots")

    # Список сообщений для удаления
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(message.message_id)

    prompt_message_id = data.get("prompt_message_id")
    if prompt_message_id:
        messages_to_delete.append(prompt_message_id)

    try:
        start_hour, start_minute, end_hour, end_minute = map(int, user_input.split())

        start_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M")
        end_time = datetime.strptime(f"{end_hour}:{end_minute}", "%H:%M")

        # Проверка, что время начала раньше времени конца
        if start_time >= end_time:
            error_message = await message.answer(
                "⚠️ Неверно введен временной интервал! ⚠️\n"
                "✍🏻 Введите время бронирования в формате ч м ч м\n"
                "Например _11 00 12 00_",
                parse_mode="Markdown",
            )
            messages_to_delete.append(error_message.message_id)
            await state.update_data(messages_to_delete=messages_to_delete)
            return

    except ValueError:
        error_message = await message.answer(
            "⚠️ Неверно введен временной интервал! ⚠️\n"
            "✍🏻 Введите время бронирования в формате ч м ч м\n"
            "Например _11 00 12 00_",
            parse_mode="Markdown",
        )
        messages_to_delete.append(error_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    # Проверка на пересечение с забронированными интервалами
    conflict = False
    for booked in booked_slots:
        booked_start = datetime.strptime(booked["start"], "%H:%M")
        booked_end = datetime.strptime(booked["end"], "%H:%M")
        if start_time < booked_end and end_time > booked_start:
            conflict = True
            break

    if conflict:
        error_message = await message.answer(
            "⚠️ Это время уже забронировано! ⚠️\n"
            "✍🏻 Введите время бронирования в формате ч м ч м\n"
            "Например _11 00 12 00_",
            parse_mode="Markdown",
        )
        messages_to_delete.append(error_message.message_id)
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    # Удаление всех сообщений перед успешным бронированием
    for msg_id in messages_to_delete:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
        except Exception:
            pass

    await message.answer(
        f"Ваше бронирование:\n"
        f"📍 {data['selected_room']}\n"
        f"📅 {data['selected_date']}\n"
        f"🕓 {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n\n"
        "Добавить название встречи?",
        reply_markup=await get_summary_keyboard(),
        parse_mode="Markdown",
    )
    await state.update_data(start_time=start_time.strftime('%H:%M'), end_time=end_time.strftime('%H:%M'))


@router.callback_query(lambda c: c.data.startswith("time_"))
async def handle_time_selection(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    free_slots = data.get("free_slots")
    selected_time = callback.data.split("_")[1]

    try:
        selected_datetime = datetime.strptime(f"{selected_date} {selected_time}", "%d.%m.%Y %H:%M")
    except ValueError:
        corrected_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        selected_datetime = datetime.strptime(f"{corrected_date} {selected_time}", "%d.%m.%Y %H:%M")

    await state.update_data(selected_time=selected_time)
    await callback.message.edit_text(
        text=(
            f"📍 *{selected_room} - {selected_date}*  📅\n\n"
            f"🕓 Выбранное время {selected_time}\n"
            f"⏳ Выберите *длительность* брони:"
        ),
        reply_markup=await generate_duration_keyboard(selected_datetime, free_slots),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data.startswith("duration_"))
async def handle_duration_selection(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    selected_time = data.get("selected_time")

    selected_duration = int(callback.data.split("_")[1])

    start_datetime = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + timedelta(minutes=selected_duration)

    start_time_formatted = start_datetime.strftime("%H:%M")
    end_time_formatted = end_datetime.strftime("%H:%M")

    await state.update_data(start_time=start_time_formatted, end_time=end_time_formatted)

    await callback.message.edit_text(
        text=f"Ваше бронирование:\n"
             f"📍 Переговорная: {selected_room}\n"
             f"📅 Дата: {selected_date}\n"
             f"🕓 Время: {start_time_formatted} - {end_time_formatted}\n\n"
             "Добавить название встречи?",
        reply_markup=await get_summary_keyboard(),
        parse_mode="Markdown",
    )

    await state.update_data(start_time=start_time_formatted, end_time=end_time_formatted)
    await state.update_data(delete_flag=True)


@router.callback_query(lambda c: c.data == "add_summary")
async def add_summary(
        callback: CallbackQuery, state: FSMContext
):
    await callback.message.edit_text(
        text="✍🏻 Введите название для вашего бронирования.",
        reply_markup=await get_manual_input_keyboard(),
    )
    # Сохраняем ID сообщения для его удаления
    await state.update_data(bot_message_id=callback.message.message_id)
    await state.set_state(BookingStates.INPUT_SUMMARY)


@router.message(F.text, BookingStates.INPUT_SUMMARY)
async def handle_summary_input(
        message: types.Message, state: FSMContext
):
    summary = message.text.strip() or "Без описания"
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    bot_message_id = data.get("bot_message_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    await state.update_data(summary=summary)

    # Удаляем сообщения бота и пользователя
    await message.delete()
    if bot_message_id:
        await message.chat.delete_message(bot_message_id)

    await message.answer(
        text=f"Ваше бронирование:\n"
             f"📍 Переговорная: {selected_room}\n"
             f"📅 Дата: {selected_date}\n"
             f"🕓 Время: {start_time} - {end_time}\n"
             f"📌 Название: {summary}\n\n"
             "Добавить описание?",
        reply_markup=await get_description_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data == "skip_summary")
async def ask_summary_handler(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    summary = data.get("summary", "Без названия")
    await callback.message.edit_text(
        text=f"Ваше бронирование:\n"
             f"📍 Переговорная: {selected_room}\n"
             f"📅 Дата: {selected_date}\n"
             f"🕓 Время: {start_time} - {end_time}\n"
             f"📌 Название: {summary}\n\n"
             "Добавить описание?",
        reply_markup=await get_description_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data == "add_description")
async def add_description_handler(
        callback: CallbackQuery, state: FSMContext
):
    await callback.message.edit_text(
        text="✍🏻 Введите описание для вашего бронирования.",
        reply_markup=await get_manual_input_keyboard(),
    )
    # Сохраняем ID сообщения для его удаления
    await state.update_data(bot_message_id=callback.message.message_id)
    await state.set_state(BookingStates.INPUT_DESCRIPTION)


@router.message(F.text, BookingStates.INPUT_DESCRIPTION)
async def handle_description_input(
        message: types.Message, state: FSMContext
):
    description = message.text.strip() or "Без описания"
    data = await state.get_data()
    bot_message_id = data.get("bot_message_id")

    await state.update_data(description=description)

    # Удаляем сообщения бота и пользователя
    await message.delete()
    if bot_message_id:
        await message.chat.delete_message(bot_message_id)  # Удаляем сообщение с запросом
    # Строим свой CallbackQuery, для перехода в confirm_booking без нажатия кнопок пользователем
    callback_query = CallbackQuery(
        id="id",
        from_user=User(id=message.from_user.id, is_bot=False, first_name=message.from_user.first_name),
        chat_instance="chat_instance",
        message=message,
        data="confirm_booking",
    )
    await confirm_booking_handler(callback_query, state=state)


@router.callback_query(lambda c: c.data == "skip_description")
async def skip_description_handler(
        callback: CallbackQuery, state: FSMContext
):
    await callback.message.delete()
    # Строим свой CallbackQuery, для перехода в confirm_booking без нажатия кнопок пользователем
    callback_query = CallbackQuery(
        id="id",
        from_user=User(id=callback.from_user.id, is_bot=False, first_name=callback.from_user.first_name),
        chat_instance="chat_instance",
        message=callback.message,
        data="confirm_booking",
    )
    await confirm_booking_handler(callback_query, state=state)


@router.callback_query(lambda c: c.data == "confirm_booking")
async def confirm_booking_handler(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    summary = data.get("summary", "Без названия")
    description = data.get("description", "Без описания")

    await callback.message.answer(
        text=f"Ваше бронирование:\n"
             f"📍 Переговорная: {selected_room}\n"
             f"📅 Дата: {selected_date}\n"
             f"🕓 Время: {start_time} - {end_time}\n"
             f"📌 Название: {summary}\n"
             f"📋 Описание: {description}",
        reply_markup=await get_confirmation_booking_keyboard(),
        parse_mode="Markdown",
    )
    await state.set_state(BookingStates.CONFIRM_BOOKING)


@router.callback_query(lambda c: c.data == "booking_confirmed", BookingStates.CONFIRM_BOOKING)
async def booking_confirmed_handler(
        callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_room = data.get("selected_room")
    selected_date = data.get("selected_date")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    summary = data.get("summary", "Без названия")
    description = data.get("description", "Без описания")

    # Рандомная задержка, для уменьшения вероятности бронирования на одно и то же время
    random_delay = random.uniform(0.5, 2)
    await asyncio.sleep(random_delay)

    start_datetime = datetime.fromisoformat(f"{selected_date}T{start_time}:00").astimezone(TIMEZONE)
    end_datetime = datetime.fromisoformat(f"{selected_date}T{end_time}:00").astimezone(TIMEZONE)

    start_of_day = datetime.combine(start_datetime.date(), time.min, tzinfo=TIMEZONE)
    end_of_day = datetime.combine(start_datetime.date(), time.max, tzinfo=TIMEZONE)
    events_today = await get_events(start_of_day, end_of_day)

    normalized_room_name = await normalize_location(selected_room)
    for event in events_today:
        event_location = await normalize_location(event.get("location", ""))
        if event_location != normalized_room_name:
            continue

        event_start = datetime.fromisoformat(event["start"]["dateTime"]).astimezone(TIMEZONE)
        event_end = datetime.fromisoformat(event["end"]["dateTime"]).astimezone(TIMEZONE)

        if max(event_start, start_datetime) < min(event_end, end_datetime):
            await callback.message.edit_text(
                text=(
                    f"❌ Невозможно забронировать. На это время уже есть бронь:\n\n"
                    f"📍 Переговорная: {selected_room}\n"
                    f"🕓 {event_start.strftime('%H:%M')} - {event_end.strftime('%H:%M')}\n"
                    f"📌 Название: {event.get('summary', 'Без названия')}\n"
                ),
                reply_markup=await get_main_keyboard(),
                parse_mode="Markdown",
            )
            await state.clear()
            return

    # Тег пользователя, который инициировал бронирование
    custom_creator = f"@{callback.from_user.username}" if callback.from_user.username else "unknown"

    event_data = {
        "summary": f"{summary}",
        "description": description,
        "start": {
            "dateTime": f"{selected_date}T{start_time}:00",
            "timeZone": "Asia/Yekaterinburg",
        },
        "end": {
            "dateTime": f"{selected_date}T{end_time}:00",
            "timeZone": "Asia/Yekaterinburg",
        },
        "location": selected_room,
    }

    try:
        await create_google_calendar_event(event_data, custom_creator)
        await callback.message.edit_text(
            text=(
                f"✅ Переговорная успешно забронирована:\n\n"
                f"📍 Переговорная: {selected_room}\n"
                f"📅 Дата: {selected_date}\n"
                f"🕓 Время: {start_time} - {end_time}\n"
                f"📌 Название: {summary}\n"
                f"📋 Описание: {description}"
            ),
            reply_markup=await get_main_keyboard(),
            parse_mode="Markdown",
        )
        await state.clear()
    except Exception as e:
        print("Ошибка при создании события: %s", str(e))
        await callback.message.edit_text(
            text=(
                f"❌ Что-то пошло не так. *Не удалось* забронировать переговорную:\n"
                f"⚠️ _Ошибка_: {str(e)}"
            ),
            reply_markup=await get_main_keyboard(),
            parse_mode="Markdown",
        )
