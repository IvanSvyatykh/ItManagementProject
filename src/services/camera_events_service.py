from pathlib import Path

import requests
from database.dto import CameraEventDto
from database.db_core import PostgresConfig, IsDBUnitOfWork
from config import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DOMAIN,
    POSTGRES_DB_NAME,
    POSTGRES_PORT,
)
from typing import Tuple


async def get_last_camera_event(
    camera_id: int, scenario_id: int, user_id: int
) -> Tuple[int, Path]:
    config = PostgresConfig(
        user_name=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        domain=POSTGRES_DOMAIN,
        port=POSTGRES_PORT,
        db_name=POSTGRES_DB_NAME,
    )

    config.create_engine()
    uow = IsDBUnitOfWork(config)
    with uow.start() as session:
        kitchen_event: CameraEventDto = (
            await session.monitoring_events_repository.get_last_camera_event(
                camera_id, scenario_id
            )
        )
    photo_path = await __get_photo(kitchen_event, user_id)
    return (len(kitchen_event.boxes_cords["bboxes"]), photo_path)


async def __get_photo(kitchen_event: CameraEventDto, user_id: int) -> Path:
    img_data = requests.get(
        f"https://api.platform-vision.is74.ru/analytics/images/draw/{kitchen_event.scenario_id}/{str(kitchen_event.timestamp).replace(' ', '%20')}/{kitchen_event.camera_id}/{kitchen_event.image_key}.jpg"
    ).content

    photo_path = Path(f"src/files/kitchen/{user_id}.jpg")
    with open(photo_path, "wb") as handler:
        handler.write(img_data)
    return photo_path
