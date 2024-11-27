from datetime import datetime
import json

from database.models import MonitoringEvents


class CameraEventDto:

    def __init__(self, monitoring_events: MonitoringEvents):
        self.__id = monitoring_events.id
        self.__timestamp = monitoring_events.timestamp
        self.__camera_id = monitoring_events.camera_id
        self.__scenario_id = monitoring_events.scenario_id
        self.__image_key = monitoring_events.image_key
        self.__boxes_cords = monitoring_events.add_data

    @property
    def camera_id(self) -> int:
        return self.__camera_id

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def scenario_id(self) -> int:
        return self.__scenario_id

    @property
    def image_key(self) -> str:
        return self.__image_key

    @property
    def boxes_cords(self) -> dict:
        return self.__boxes_cords
