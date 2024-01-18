import uuid
import uvicorn
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src import crud, schemas
from src.database import get_session

app = FastAPI()


class Tags(Enum):
    couriers = "Couriers"
    orders = "Orders"


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@app.post("/courier", tags=[Tags.couriers], summary="Регистрация нового курьера")
def create_courier(courier: schemas.CourierIn, db: Session = Depends(get_db)):
    """
    ### Регистрация нового курьера в системе

    - **name**: `str` - имя курьера
    - **districts**: `list[str]` - массив районов, в которых курьер имеет возможность принимать заказ
    """
    districts = list(set(d.lower() for d in courier.districts))  # избавляемся от дубликатов районов
    db_courier = courier
    db_courier.districts = districts  # передаем в модель курьера массив районов без дубликатов
    db_courier = crud.create_courier(db, db_courier)  # добавляем курьера в БД
    return {"message": f"Courier '{db_courier.name}' is registered"}


@app.get("/courier", response_model=list[schemas.CourierBase], tags=[Tags.couriers], summary="Получение информации о всех курьерах")
def get_couriers(db: Session = Depends(get_db)):
    """
    ### Получение информации о всех курьерах в системе

    Возвращает массив элементов со следующими полями:
    - **id**: `uuid` - уникальный идентификатор курьера
    - **name**: `str` - имя курьера
    """
    return crud.get_couriers(db) # получаем из БД и возвращаем информацию по всем курьерам


@app.get("/courier/{id}", response_model=schemas.Courier, tags=[Tags.couriers], summary="Получение информации о курьере")
def get_courier(id: uuid.UUID, db: Session = Depends(get_db)):
    """
    ### Получение подробной информации о курьере

    Для получения информации о курьере необходимо указать **id**: `uuid` - уникальный идентификатор курьера

    Возвращает следующую информацию:
    - **id**: `uuid` - уникальный идентификатор курьера
    - **name**: `str` - имя курьера
    - **active_order**: `dict` - информация об активном заказе. Если такого заказа нет, возвращает `None`
        - **order_id**: `uuid` - уникальный идентификатор заказа
        - **order_name**: `str` - наименование заказа
    - **avg_order_complete_time**: `datetime` - среднее время выполнения заказа
    - **avg_day_orders**: `int` - среднее количество выполненных заказов за день работы
    """
    db_courier = crud.get_courier(db, id)  # попытка получения курьера из БД
    if db_courier is not None:
        return db_courier  # курьер найден - возвращаем курьера
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Courier does not exist')  # курьер не найден - возвращаем ошибку


@app.post("/order", response_model=schemas.OrderCreated, tags=[Tags.orders], summary="Публикация заказа")
def create_order(order: schemas.OrderIn, db: Session = Depends(get_db)):
    """
    ### Публикация заказа в системе

    Для публикации нужно передать следующую информацию:
    - **name**: `str` - имя заказа
    - **district**: `str` - район заказа

    Если в базе есть курьер, который работает в указанном районе и не имеет активного заказа, заказ публикуется, для заказа назначается свободный курьер. Запрос возвращает поля:
    - **order_id**: `uuid` - уникальный идентификатор заказа
    - **courier_id**: `uuid` - уникальный идентификатор назначенного курьера

    Если подходящий курьер не найден, запрос возвращает ошибку
    """
    order = crud.create_order(db, order) # попытка создать заказ. Если заказ создан - возвращаем информацию по нему
    return order


@app.get("/order/{id}", response_model=schemas.OrderInfo, tags=[Tags.orders], summary="Получение информации о заказе")
def get_order(id: uuid.UUID, db: Session = Depends(get_db)):
    """
    ### Получение информации о конкретном заказе

    Для получения информации нужно передать в запросе **id**: `uuid` - уникальный идентификатор заказа

    Если такой заказ существует, запрос вернёт следующие поля:
    - **courier_id**: `uuid` - идентификатор курьера, назначенного для этого заказа
    - **status**: `int` - статус заказа; 1 - заказ в работе, 2 - заказ завершен
    """
    order = crud.get_order(db, id)  # пробуем получить заказ из БД
    if order is not None:
        return order  # заказ существует, возвращаем информацию
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Order does not exist')  # заказ не существует, возвращаем ошибку


@app.post("/order/{id}", tags=[Tags.orders], summary="Завершение заказа")
def complete_order(id: uuid.UUID, db: Session = Depends(get_db)):
    """
    ### Завершение заказа

    Запрос меняет статус заказа на 'Завершен'. В запросе нужно передать **id**: `uuid` - идентификатор заказа.
    Если заказ не существует или уже завершен, запрос вернёт ошибку
    """
    result = crud.complete_order(db, id)  # пробуем завершить заказ, если завершение заказа прошло успешно, функция вернет True
    if result:
        return {"message": "OK"}

    if not result:  # заказ не найден или уже завершен - возвращаем ошибку
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='The order does not exist or has already been completed')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)