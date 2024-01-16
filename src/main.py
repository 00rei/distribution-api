import uuid

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/courier")
def create_courier(courier: schemas.CourierBase, db: Session = Depends(get_db)):
    districts = list(set(d.lower() for d in courier.districts))
    db_courier = courier
    db_courier.districts = districts
    db_courier = crud.create_courier(db, db_courier)
    return {"message": f"Курьер '{db_courier.name}' зарегистрирован в системе"}


@app.get("/courier", response_model=list[schemas.CourierOut])
def get_couriers(db: Session = Depends(get_db)):
    return crud.get_couriers(db)
