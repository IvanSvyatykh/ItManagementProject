from datetime import datetime
from pathlib import Path
from datetime import timedelta
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
from services.utils.grapics_makers import create_hist_of_disribution


async def __get_photo_of_kitchen(
    kitchen_event: CameraEventDto, user_id: int
) -> Path:
    img_data = requests.get(
        f"https://api.platform-vision.is74.ru/analytics/images/draw/{kitchen_event.scenario_id}/{str(kitchen_event.timestamp).replace(' ', '%20')}/{kitchen_event.camera_id}/{kitchen_event.image_key}.jpg"
    ).content

    photo_path = Path(f"src/files/kitchen_photo/kitchen_{user_id}.jpg")
    with open(photo_path, "wb") as handler:
        handler.write(img_data)
    return photo_path


async def get_people_disribution_on_kitchen_by_day(
    camera_id: int, scenario_id: int, date: datetime, user_id: int
) -> Path:
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
        events = session.monitoring_events_repository.get_day_camera_event(
            camera_id, scenario_id, date.date()
        )
    y = []
    x = []
    for event in events:
        y.append(len(event.boxes_cords["bboxes"]))
        x.append(event.timestamp + timedelta(hours=5))

    path = Path(f"src/files/kitchen_photo/stat_{user_id}.png")

    await create_hist_of_disribution(y_data=y, x_data=x, path_to_png=path)
    return path


async def get_people_disribution_on_kitchen_by_week(
    camera_id: int, scenario_id: int, date: datetime, user_id: int
) -> Path:
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
        events = session.monitoring_events_repository.get_day_camera_event(
            camera_id, scenario_id, date.date()
        )
    y = []
    x = []
    for event in events:
        y.append(len(event.boxes_cords["bboxes"]))
        x.append(event.timestamp + timedelta(hours=5))

    path = Path(f"src/files/kitchen_photo/stat_{user_id}.png")

    await create_hist_of_disribution(y_data=y, x_data=x, path_to_png=path)
    return path


async def get_people_on_kitchen(
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
            session.monitoring_events_repository.get_last_camera_event(
                camera_id, scenario_id
            )
        )
    photo_path = await __get_photo_of_kitchen(kitchen_event, user_id)
    return (len(kitchen_event.boxes_cords["bboxes"]), photo_path)
