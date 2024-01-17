from sqlalchemy import Column, Integer, UUID, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from .database import Base


class Courier(Base):
    __tablename__ = "couriers"

    id = Column(UUID, primary_key=True)
    name = Column(String)
    avg_order_complete_time = Column(Integer, default=0)
    avg_day_orders = Column(Integer, default=0)

    orders = relationship("Order", back_populates="courier")
    courier_districts = relationship("District", back_populates="district_couriers", secondary="couriers_districts")


class District(Base):
    __tablename__ = "districts"

    id = Column(UUID, primary_key=True)
    name = Column(String, unique=True)

    orders = relationship("Order", back_populates="district")
    district_couriers = relationship("Courier", back_populates="courier_districts", secondary="couriers_districts")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True)
    name = Column(String)
    district_id = Column(UUID, ForeignKey("districts.id"))
    courier_id = Column(UUID, ForeignKey("couriers.id"))
    status = Column(Integer)
    date_publication = Column(DateTime, default=now())
    date_completion = Column(DateTime, default=None)

    district = relationship("District", back_populates="orders")
    courier = relationship("Courier", back_populates="orders")


class CourierDistrict(Base):
    __tablename__ = "couriers_districts"

    courier_id = Column(UUID, ForeignKey("couriers.id"), primary_key=True)
    district_id = Column(UUID, ForeignKey("districts.id"), primary_key=True)
