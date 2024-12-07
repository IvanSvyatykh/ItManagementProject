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
from services.utils.grapics_makers import create_hist_of_day_disribution


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
        events = await session.monitoring_events_repository.get_day_camera_events(
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
