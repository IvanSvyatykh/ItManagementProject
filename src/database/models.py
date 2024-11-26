from sqlalchemy import Column, TIMESTAMP, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MonitoringEvents(Base):
    __tablename__ = "my_view"
    timestamp = Column(TIMESTAMP)
    camera_id = Column(Integer)
    image_key = Column(String)
