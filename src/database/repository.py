from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import MonitoringEvents


class MonitoringEventsRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_last_camera_event(self, camera_id: int) -> MonitoringEvents:
        latest_event = (
            self.session.query(MonitoringEvents)
            .filter_by(camera_id=camera_id)
            .order_by(MonitoringEvents.timestamp.desc())
            .first()
        )
        return latest_event
