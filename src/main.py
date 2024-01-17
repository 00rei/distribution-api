import uuid

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/courier")
def create_courier(courier: schemas.CourierIn, db: Session = Depends(get_db)):
    districts = list(set(d.lower() for d in courier.districts))
    db_courier = courier
    db_courier.districts = districts
    db_courier = crud.create_courier(db, db_courier)
    return {"message": f"Курьер '{db_courier.name}' зарегистрирован в системе"}


@app.get("/courier", response_model=list[schemas.CourierBase])
def get_couriers(db: Session = Depends(get_db)):
    return crud.get_couriers(db)


@app.get("/courier/{id}", response_model=schemas.Courier)
def get_courier(id: uuid.UUID, db: Session = Depends(get_db)):
    db_courier = crud.get_courier(db, id)
    if db_courier is not None:
        return db_courier
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Courier does not exist')


@app.post("/order", response_model=schemas.OrderCreated)
def create_order(order: schemas.OrderIn, db: Session = Depends(get_db)):
    order = crud.create_order(db, order)
    return order


@app.get("/order/{id}", response_model=schemas.OrderInfo)
def get_order(id: uuid.UUID, db: Session = Depends(get_db)):
    order = crud.get_order(db, id)
    if order is not None:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order does not exist')


@app.post("/order/{id}")
def complete_order(id: uuid.UUID, db: Session = Depends(get_db)):
    result = crud.complete_order(db, id)
    if result:
        return {"message": "OK"}

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The order does not exist or has already been completed')
