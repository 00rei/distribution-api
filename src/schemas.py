import uuid
from datetime import timedelta, datetime

from pydantic import BaseModel, UUID4, Field


class DistrictBase(BaseModel):
    name: str


class District(DistrictBase):
    id: UUID4


class OrderBase(BaseModel):
    name: str


class OrderIn(OrderBase):
    district: str


class OrderOut(BaseModel):
    order_id: uuid.UUID
    order_name: str


class OrderCreated(BaseModel):
    order_id: uuid.UUID
    courier_id: uuid.UUID


# class Order(OrderBase):
#     id: UUID4
#     status: int
#     courier: Courier
#     date_publication: datetime
#     date_completion: datetime | None


# class CourierBase(BaseModel):
#     id: UUID4
#     name: str

class CourierBase(BaseModel):
    id: uuid.UUID
    name: str


class CourierIn(BaseModel):
    name: str
    districts: list[str] = set()


class Courier(CourierBase):
    active_order: OrderOut | None = None
    avg_order_complete_time: timedelta | None
    avg_day_orders: int | None
