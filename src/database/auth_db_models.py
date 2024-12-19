from sqlalchemy import (
    Column,
    String,
    BOOLEAN,
    TIMESTAMP,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    phone_number = Column(String(32), primary_key=True)
    is_active = Column(BOOLEAN)


class Statistics(Base):
    __tablename__ = "statistics"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    action_type = Column(String(32), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    chat_id = Column(Integer, nullable=False)
