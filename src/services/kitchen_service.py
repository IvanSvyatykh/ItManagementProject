from datetime import datetime, timedelta
from pathlib import Path
from database.db_core import PostgresConfig, IsDBUnitOfWork
from config import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DOMAIN,
    POSTGRES_DB_NAME,
    POSTGRES_PORT,
)
from typing import Tuple
from services.utils.grapics_makers import (
    create_hist_of_day_disribution,
    create_hist_of_week_disribution,
)


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
        events = await session.monitoring_events_repository.get_day_camera_event(
            camera_id, scenario_id, date.date()
        )
    y = []
    x = []
    for event in events:
        y.append(len(event.boxes_cords["bboxes"]))
        x.append(event.timestamp + timedelta(hours=5))
    if len(x) == 0 or len(y) == 0:
        return None
    path = Path(f"src/files/stat/{user_id}_stat_day.png")

    await create_hist_of_day_disribution(
        y_data=y, x_data=x, path_to_png=path
    )
    return path


async def __get_start_end_last_week(
    current_date: datetime,
) -> Tuple[datetime, datetime]:

    start = current_date.date() - timedelta(
        days=(current_date.date().isoweekday()) + 6
    )
    end = current_date.date() - timedelta(
        days=(current_date.date().isoweekday())
    )

    return (start, end)


async def get_people_disribution_on_kitchen_by_week(
    camera_id: int,
    scenario_id: int,
    current_date: datetime,
    user_id: int,
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
    start_last_week, end_last_week = await __get_start_end_last_week(
        current_date
    )
    with uow.start() as session:
        events = await session.monitoring_events_repository.get_week_camera_event(
            camera_id, scenario_id, start_last_week, end_last_week
        )
    y = []
    x = []
    for event in events:
        y.append(len(event.boxes_cords["bboxes"]))
        x.append(event.timestamp + timedelta(hours=5))

    if len(x) == 0 or len(y) == 0:
        return None
    path = Path(f"src/files/kitchen_photo/{user_id}_stat_week.png")

    await create_hist_of_week_disribution(
        y_data=y, x_data=x, path_to_png=path
    )
    return path
