from sqlalchemy import func
from sqlalchemy.orm import Session

from database.dto import CameraEventDto
from database.models import MonitoringEvents


class MonitoringEventsRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_last_camera_event(
        self, camera_id: int, scenario_id: int
    ) -> CameraEventDto:
        latest_event: MonitoringEvents = (
            self.session.query(MonitoringEvents)
            .filter_by(camera_id=camera_id, scenario_id=scenario_id)
            .order_by(MonitoringEvents.timestamp.desc())
            .first()
        )
        if latest_event is None:
            return None
        return CameraEventDto(latest_event)
