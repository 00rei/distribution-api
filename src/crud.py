import uuid
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas


def get_district(db: Session, district_param: str) -> schemas.District | None:
    district = db.query(models.District).filter(models.District.name == district_param.lower()).first()
    if district is None:
        return None

    district.name = district.name.title()
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


def create_courier(db: Session, courier: schemas.CourierBase):
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


def get_couriers(db: Session):
    return db.query(models.Courier).all()
