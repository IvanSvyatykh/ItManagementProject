from sqlalchemy import Column, TIMESTAMP, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MonitoringEvents(Base):
    __tablename__ = "monitoring_events"
    __table_args__ = {"schema": "analytics"}
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    camera_id = Column(Integer)
    scenario_id = Column(Integer)
    image_key = Column(String)
    add_data = Column(JSON)
