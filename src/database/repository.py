from datetime import datetime
from typing import List
from sqlalchemy import func, insert
from sqlalchemy.orm import Session
from database.dto import CameraEventDto
from database.is_db_models import MonitoringEvents

from database.auth_db_models import Statistics, Users


class AuthRepository:

    def __init__(self, session: Session):
        self.session = session

    async def check_if_exists(self, phone_number: str) -> bool:
        user: Users = (
            self.session.query(Users)
            .filter_by(phone_number=phone_number)
            .first()
        )
        if user is None:
            return None

        print(user.is_active)
        return user.is_active


class StatRepository:
    def __init__(self, session: Session):
        self.session = session

    async def insert(
        self, action_type: str, datetime: datetime, chat_id: str
    ) -> int:
        return self.session.scalar(
            insert(Statistics)
            .values(
                action_type=action_type,
                timestamp=datetime,
                chat_id=chat_id,
            )
            .returning(Statistics)
        )


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

    async def get_day_camera_events(
        self, camera_id: int, scenario_id: int, target_date: datetime
    ) -> List[CameraEventDto]:
        event_by_date: List[MonitoringEvents] = (
            self.session.query(MonitoringEvents)
            .filter_by(
                camera_id=camera_id,
                scenario_id=scenario_id,
            )
            .filter(func.date(MonitoringEvents.timestamp) == target_date)
            .order_by(MonitoringEvents.timestamp)
            .all()
        )
        if event_by_date is None:
            return None

        return [CameraEventDto(event) for event in event_by_date]
