from sqlalchemy import Column, String, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    phone_number = Column(String, primary_key=True)
    is_active = Column(BOOLEAN)
