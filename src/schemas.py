import uuid
from datetime import timedelta, datetime, time

from pydantic import BaseModel, UUID4, Field, field_validator


class DistrictBase(BaseModel):
    name: str


class District(DistrictBase):
    id: UUID4


class OrderBase(BaseModel):
    name: str = Field(examples=["order name"], min_length=1)


class OrderInfo(BaseModel):
    courier_id: uuid.UUID
    status: int


class OrderIn(OrderBase):
    district: str = Field(examples=["district"], min_length=1)


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
    name: str = Field(examples=["Courier Name"], min_length=1)
    districts: list[str] = Field(examples=[["district name one", "district name two", "district name three"]], min_length=1)


class Courier(CourierBase):
    active_order: OrderOut | None = None
    avg_order_complete_time: timedelta | None
    avg_day_orders: int | None

    @field_validator("avg_order_complete_time")
    def validate_avg_order_complete_time(cls, v):
        return str(v)
