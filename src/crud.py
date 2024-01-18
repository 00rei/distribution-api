import datetime
import uuid
from enum import IntEnum
from math import floor

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas


class Status(IntEnum):
    IN_PROGRESS = 1
    COMPLETED = 2


def get_district(db: Session, district_param: str) -> schemas.District | None:
    district = db.query(models.District).filter(models.District.name == district_param.lower()).first()
    if district is None:
        return None

    return district


def create_or_get_district(db: Session, district_name: schemas.DistrictBase):
    db_district = get_district(db, district_name)
    if db_district is not None:
        return db_district

    db_district = models.District(name=district_name.lower(), id=uuid.uuid4())
    db.add(db_district)
    db.commit()
    db.refresh(db_district)
    return db_district


def create_courier(db: Session, courier: schemas.CourierIn):
    id_courier = uuid.uuid4()
    db_courier = models.Courier(id=id_courier, name=courier.name)
    db.add(db_courier)
    db.commit()

    districts = courier.districts
    for district in districts:
        db_district = create_or_get_district(db, district)
        db_district.name = db_district.name.lower()
        courier_district = models.CourierDistrict(courier_id=id_courier, district_id=db_district.id)
        db.add(courier_district)

    db.commit()
    db.refresh(db_courier)
    return db_courier


def get_active_order_by_courier(db: Session, courier: schemas.Courier):
    try:
        db_order = db.query(models.Order).filter(models.Order.status == Status.IN_PROGRESS,
                                                 models.Order.courier_id == courier.id).first()
    except Exception:
        db_order = None
    return db_order


def get_couriers(db: Session):
    return db.query(models.Courier).all()


def get_courier(db: Session, id: str):
    try:
        db_courier = db.query(models.Courier).filter(models.Courier.id == id).first()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='`id` parameter must be of the `uuid` format')

    if not db_courier:
        return None

    schema_order = None
    db_active_order = get_active_order_by_courier(db, db_courier)

    if db_active_order is not None:
        schema_order = schemas.OrderOut(order_id=db_active_order.id, order_name=db_active_order.name)

    courier = schemas.Courier(id=db_courier.id,
                              name=db_courier.name,
                              avg_order_complete_time=db_courier.avg_order_complete_time,
                              avg_day_orders=db_courier.avg_day_orders,
                              active_order=schema_order)
    return courier


def create_order(db: Session, order: schemas.OrderIn) -> schemas.OrderCreated:
    district = get_district(db, order.district)
    try:
        couriers = district.district_couriers
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No suitable courier found')
    list_couriers: list[models.Courier] = []

    for courier in couriers:
        if get_active_order_by_courier(db, courier) is None:
            list_couriers.append(courier)

    if not list_couriers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No suitable courier found')

    # courier = min(list_couriers, key=lambda x: x.avg_day_orders)  # выбираем курьера, который выполняет больше заказов за день
    courier = min(list_couriers, key=lambda x: x.avg_order_complete_time)  # выбираем курьера, который выполняет заказы быстрее

    order_id = uuid.uuid4()
    db_order = models.Order(id=order_id, name=order.name, district_id=district.id, courier_id=courier.id,
                            status=Status.IN_PROGRESS)
    db.add(db_order)
    db.commit()

    order_created = schemas.OrderCreated(order_id=order_id, courier_id=courier.id)

    return order_created


def get_order(db: Session, order_id: uuid.UUID):
    try:
        db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='`id` parameter must be of the `uuid` format')

    if not db_order:
        return None

    return db_order


def complete_order(db: Session, order_id: uuid.UUID):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None

    if db_order.status == Status.COMPLETED:
        return None

    db_order.status = Status.COMPLETED
    db_order.date_completion = datetime.datetime.now()
    db.commit()

    db_courier = db.query(models.Courier).filter(models.Courier.id == db_order.courier_id).first()
    courier_orders = db_courier.orders

    list_completed_orders: list[models.Order] = []
    avg_order_complete_time = 0
    count_orders = {}

    for order in courier_orders:
        if order.status == Status.COMPLETED:
            list_completed_orders.append(order)
            time = order.date_completion - order.date_publication
            avg_order_complete_time += time.seconds

    for order in list_completed_orders:
        order_publication_date = order.date_publication.date()
        if order_publication_date in count_orders:
            count_orders[order_publication_date] += 1
        else:
            count_orders[order_publication_date] = 1

    avg_order_complete_time = avg_order_complete_time / len(list_completed_orders)
    avg_day_orders = floor(sum(count_orders.values()) / len(count_orders))

    db_courier.avg_order_complete_time = avg_order_complete_time
    db_courier.avg_day_orders = avg_day_orders

    db.commit()

    return True
