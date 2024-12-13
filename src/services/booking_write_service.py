import json
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from config import (
    SERVICE_ACCOUNT_FILE,
    SCOPES,
    CALENDAR_ID,
)


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


async def create_google_calendar_event(event_data):
    async with Aiogoogle(service_account_creds=CREDS) as aiogoogle:
        calendar_api = await aiogoogle.discover("calendar", "v3")
        try:
            response = await aiogoogle.as_service_account(
                calendar_api.events.insert(calendarId=CALENDAR_ID, json=event_data)
            )
            return response
        except Exception as e:
            raise Exception(f"Ошибка при создании события: {str(e)}")
