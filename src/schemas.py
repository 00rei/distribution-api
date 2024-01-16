import uuid
from datetime import timedelta, datetime

from pydantic import BaseModel, UUID4


class DistrictBase(BaseModel):
    name: str


class District(DistrictBase):
    id: UUID4


class CourierBase(BaseModel):
    name: str
    districts: list[str] = set()


class CourierOut(BaseModel):
    id: UUID4
    name: str


class Courier(CourierBase):
    id: UUID4
    avg_order_complete_time: timedelta | None
    avg_day_orders: int | None


class OrderBase(BaseModel):
    name: str
    district: District


class OrderCreated(BaseModel):
    id: UUID4
    courier: Courier


class Order(OrderBase):
    id: UUID4
    status: int
    courier: Courier
    date_publication: datetime
    date_completion: datetime | None
