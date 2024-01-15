from sqlalchemy import Column, Integer, UUID, String, DateTime, Boolean

from .database import Base


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(UUID, primary_key=True)
    name = Column(String)
