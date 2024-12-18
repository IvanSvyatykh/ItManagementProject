from datetime import datetime, timedelta
from pathlib import Path
from database.db_core import IsDBUnitOfWork
from services.utils.grapics_makers import create_hist_of_day_disribution


async def get_people_disribution_on_kitchen_by_day(
    camera_id: int, scenario_id: int, date: datetime
) -> Path:
    path = Path(f"src/files/stat/{date.date()}.png")
    if path.exists():
        return path
    path_to_remove = Path(
        f"src/files/stat/{date.date()-timedelta(days=4)}.png"
    )
    if path_to_remove.exists():
        path_to_remove.unlink()

    uow = IsDBUnitOfWork()
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

    await create_hist_of_day_disribution(
        y_data=y, x_data=x, path_to_png=path
    )
    return path
