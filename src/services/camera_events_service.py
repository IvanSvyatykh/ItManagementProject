from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

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


async def get_last_camera_event(camera_id: int) -> dict:
    photo_path = Path(f"src/files/photos/{camera_id}.jpg")
    meta = pd.read_csv(f"src/files/photos/{camera_id}.csv")
    return {
        "people_nums": meta["people_nums"][0],
        "path_to_photo": photo_path,
        "meta": meta["meta"][0],
    }


def update_camera_photo(camera_id: int, scenario_id: int) -> dict:
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
    meta = (
        "Внимание, последняя фотография была сделана более 2 минут назад, данные могу быть не актуальными."
        if (
            datetime.now() - (kitchen_event.timestamp + timedelta(hours=5))
        ).total_seconds()
        > 120
        else None
    )
    photo_path = __get_photo(kitchen_event)
    pd.DataFrame.from_dict(
        {
            "meta": [meta],
            "people_nums": [len(kitchen_event.boxes_cords["bboxes"])],
        }
    ).to_csv(f"src/files/photos/{kitchen_event.camera_id}.csv")
    return {
        "people_nums": len(kitchen_event.boxes_cords["bboxes"]),
        "path_to_photo": photo_path,
        "meta": meta,
    }


def __get_photo(kitchen_event: CameraEventDto) -> Path:
    img_data = requests.get(
        f"https://api.platform-vision.is74.ru/analytics/images/draw/{kitchen_event.scenario_id}/{str(kitchen_event.timestamp).replace(' ', '%20')}/{kitchen_event.camera_id}/{kitchen_event.image_key}.jpg"
    ).content

    photo_path = Path(f"src/files/photos/{kitchen_event.camera_id}.jpg")
    with open(photo_path, "wb") as handler:
        handler.write(img_data)
    return photo_path
