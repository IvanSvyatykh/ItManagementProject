import json
from datetime import datetime, time
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
import pytz
from config import SERVICE_ACCOUNT_FILE, SCOPES, CALENDAR_ID
from services.camera_events_service import get_last_camera_event
from config import CHILL_ZONE_SEVEN, BLA_BLA, TEROCHNAYA

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
    "7проектор": "Зона отдыха 7 этаж",
    "7упроектора": "Зона отдыха 7 этаж",
    "7этупроектор": "Зона отдыха 7 этаж",
    "7этажупроектор": "Зона отдыха 7 этаж",
    "7упроектор": "Зона отдыха 7 этаж",
    "7этажупроектора": "Зона отдыха 7 этаж",
    "7ойэтажупроектора": "Зона отдыха 7 этаж",
    "7этупроектора": "Зона отдыха 7 этаж",
    "7ойэтупроектора": "Зона отдыха 7 этаж",
    "7этпроектор": "Зона отдыха 7 этаж",
    "7ойэтпроектор": "Зона отдыха 7 этаж",
    # Спортивная
    "спортивная": "Бла-Бла",
    "спорткомната": "Бла-Бла",
    "спортивнаякомната": "Бла-Бла",
    # Без указания места
    "безуказанияместа": "Без указания места",
}

ROOMS_ID = {
    "Тет-а-тет": BLA_BLA,
    "Бла-Бла": BLA_BLA,
    "Зона отдыха 7 этаж": CHILL_ZONE_SEVEN,
    "7 этаж у проектора": CHILL_ZONE_SEVEN,
    "Спортивная": BLA_BLA,
    "Терочная": TEROCHNAYA,
}

MESSAGE_LIMIT = 1000
TIMEZONE = pytz.timezone("Asia/Yekaterinburg")

with open(SERVICE_ACCOUNT_FILE, "r") as f:
    service_account_info = json.load(f)

CREDS = ServiceAccountCreds(
    type=service_account_info.get("type"),
    project_id=service_account_info.get("project_id"),
    private_key_id=service_account_info.get("private_key_id"),
    private_key=service_account_info.get("private_key").replace(
        "\\n", "\n"
    ),
    client_email=service_account_info.get("client_email"),
    client_id=service_account_info.get("client_id"),
    auth_uri=service_account_info.get("auth_uri"),
    token_uri=service_account_info.get("token_uri"),
    auth_provider_x509_cert_url=service_account_info.get(
        "auth_provider_x509_cert_url"
    ),
    client_x509_cert_url=service_account_info.get("client_x509_cert_url"),
    scopes=SCOPES,
    subject=None,
)


async def get_booking_status(room_name: str, scenario_id: int) -> dict:
    room_info = await get_last_camera_event(
        camera_id=ROOMS_ID[room_name]
    )
    status = "🟢" if room_info["people_nums"] == 0 else "🔴"
    next_events = await get_next_event(room_name)

    return {
        "status": status,
        "people_count": room_info["people_nums"],
        "next_booking_time": next_events,
        "photo_path": room_info["path_to_photo"],
        "meta": room_info["meta"],
    }


def split_message_into_pages(
    text: str, limit: int = MESSAGE_LIMIT
) -> list[str]:
    lines = text.split("\n")
    pages, current_page = [], []

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
    location = "".join(
        filter(str.isalnum, location.lower().replace(" ", ""))
    )

    return LOCATION_MAP.get(location, location)


async def format_event(event: dict) -> str:
    start = datetime.fromisoformat(event["start"]["dateTime"]).astimezone(
        TIMEZONE
    )
    end = datetime.fromisoformat(event["end"]["dateTime"]).astimezone(
        TIMEZONE
    )
    location = await normalize_location(
        event.get("location", "Без указания места")
    )
    return f"{location} - {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}"


async def get_events(
    start_date: datetime, end_date: datetime
) -> list[dict]:
    async with Aiogoogle(service_account_creds=CREDS) as aiogoogle:
        calendar = await aiogoogle.discover("calendar", "v3")
        time_min = start_date.astimezone(TIMEZONE).isoformat()
        time_max = end_date.astimezone(TIMEZONE).isoformat()

        response = await aiogoogle.as_service_account(
            calendar.events.list(
                calendarId=CALENDAR_ID,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
        )
        return response.get("items", [])


async def get_next_event(location: str) -> list[dict]:
    now = datetime.now(TIMEZONE)
    start_of_day = datetime.combine(now.date(), time.min, tzinfo=TIMEZONE)
    end_of_day = datetime.combine(now.date(), time.max, tzinfo=TIMEZONE)

    events_today = await get_events(start_of_day, end_of_day)
    matched_events = []

    for event in events_today:
        if location.lower() in (
            (await normalize_location(event.get("location", ""))).lower()
        ):
            start_time = (
                datetime.fromisoformat(event["start"]["dateTime"])
                .astimezone(TIMEZONE)
                .strftime("%H:%M")
            )
            end_time = (
                datetime.fromisoformat(event["end"]["dateTime"])
                .astimezone(TIMEZONE)
                .strftime("%H:%M")
            )

            matched_events.append(
                {
                    "location": location,
                    "start_time": start_time,
                    "end_time": end_time,
                }
            )

    matched_events.sort(key=lambda x: x["start_time"])
    return matched_events
