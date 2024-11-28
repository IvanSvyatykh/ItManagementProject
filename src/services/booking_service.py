from datetime import datetime, time
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pytz
import re
import random

from src.config import (
    SERVICE_ACCOUNT_FILE,
    SCOPES,
    CALENDAR_ID,
)

LOCATION_MAP = {
    # Бла-Бла
    "блабла": "Бла-Бла",
    "блаблакомната": "Бла-Бла",

    # Тет-а-тет
    "тетатет": "Тет-а-тет",
    "тетатетошная": "Тет-а-тет",

    # Терочная
    "терочная": "Терочная",
    "тёрочная": "Терочная",

    # Зона отдыха 7 этаж
    "зонаотдыха7": "Зона отдыха 7 этаж",
    "зонаотдыха7ой": "Зона отдыха 7 этаж",
    "зонаотдыха7эт": "Зона отдыха 7 этаж",
    "зонаотдыха7ойэт": "Зона отдыха 7 этаж",
    "зонаотдыха7этаж": "Зона отдыха 7 этаж",
    "зонаотдыха7ойэтаж": "Зона отдыха 7 этаж",
    "7зонаотдыха": "Зона отдыха 7 этаж",
    "7этзонаотдыха": "Зона отдыха 7 этаж",
    "7ойэтзонаотдыха": "Зона отдыха 7 этаж",
    "7этажзонаотдыха": "Зона отдыха 7 этаж",
    "7ойэтажзонаотдыха": "Зона отдыха 7 этаж",

    # 7 этаж у проектора
    "7проектор": "7 этаж у проектора",
    "7упроектора": "7 этаж у проектора",
    "7этупроектор": "7 этаж у проектора",
    "7этажупроектор": "7 этаж у проектора",
    "7упроектор": "7 этаж у проектора",
    "7этажупроектора": "7 этаж у проектора",
    "7ойэтажупроектора": "7 этаж у проектора",
    "7этупроектора": "7 этаж у проектора",
    "7ойэтупроектора": "7 этаж у проектора",
    "7этпроектор": "7 этаж у проектора",
    "7ойэтпроектор": "7 этаж у проектора",

    # Спортивная
    "спортивная": "Спортивная",
    "спорткомната": "Спортивная",
    "спортивнаякомната": "Спортивная",

    # Без указания места
    "безуказанияместа": "Без указания места",
}

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)
calendar_id = CALENDAR_ID

MESSAGE_LIMIT = 1000
TIMEZONE = pytz.timezone("Asia/Yekaterinburg")


def get_random_people_count() -> int:
    return random.randint(0, 4)


async def get_booking_status(room_name: str, current_time: datetime) -> dict:
    people_count = get_random_people_count()

    if people_count == 0:
        status = "🟢"
    else:
        status = "🔴"

    next_booking_time = await get_next_event(room_name)

    return {
        'status': status,
        'people_count': people_count,
        'next_booking_time': next_booking_time
    }


def split_message_into_pages(text: str, limit: int = MESSAGE_LIMIT) -> list[str]:
    lines = text.split("\n")
    pages = []
    current_page = []

    for line in lines:
        if sum(len(l) + 1 for l in current_page) + len(line) + 1 <= limit:
            current_page.append(line)
        else:
            pages.append("\n".join(current_page))
            current_page = [line]

    if current_page:
        pages.append("\n".join(current_page))

    return pages


async def normalize_location(location: str) -> str:
    location = ''.join(filter(str.isalnum, location.lower().replace(' ', '')))
    return LOCATION_MAP.get(location, location)


async def format_event(event: dict) -> str:
    start = datetime.fromisoformat(event['start']['dateTime']).astimezone(TIMEZONE)
    end = datetime.fromisoformat(event['end']['dateTime']).astimezone(TIMEZONE)
    location = event.get('location', 'Без указания места')
    location = await normalize_location(location)
    return f"{location} - {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}"


async def get_events(start_date: datetime, end_date: datetime) -> list[str]:
    time_min = start_date.astimezone(TIMEZONE).isoformat(timespec='seconds')
    time_max = end_date.astimezone(TIMEZONE).isoformat(timespec='seconds')

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return [await format_event(event) for event in events]


async def get_next_event(location: str) -> str:
    now = datetime.now(TIMEZONE)
    normalized_location = await normalize_location(location)

    start_of_day = datetime.combine(now.date(), time.min, tzinfo=TIMEZONE)
    end_of_day = datetime.combine(now.date(), time.max, tzinfo=TIMEZONE)

    events_today = await get_events(start_of_day, end_of_day)
    for event in events_today:
        if normalized_location in event:
            match = re.findall(r'\d{2}:\d{2}', event)
            if match and len(match) == 2:
                event_start_time = datetime.strptime(match[0], '%H:%M').replace(
                    year=now.year, month=now.month, day=now.day, tzinfo=TIMEZONE
                )
                if event_start_time > now:
                    return f"{normalized_location} - {match[0]} - {match[1]}"
    return f"{normalized_location} - На сегодня нет брони"
