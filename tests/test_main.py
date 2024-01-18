from fastapi.testclient import TestClient

from src.database import get_session, drop_test_table, create_test_table
from src.main import app, get_db

drop_test_table()
create_test_table()


def override_get_db():
    try:
        db = get_session('test')
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_courier():
    response = client.post("/courier", json={
        "name": "Иванов Иван",
        "districts": [
            "Центральный",
            "Силикатный",
            "Поток",
            "Индустриальный"
        ]
    })
    assert response.status_code == 200, response.text

    response = client.get("/courier")
    assert response.status_code == 200, response.text
    data = response.json()
    id = data[0]['id']
    assert data[0]['name'] == 'Иванов Иван', data[0]['name']

    response = client.get(f"/courier/{id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['active_order'] is None, data['active_order']
    assert data['id'] == id, data['id']


def test_create_and_complete_order():
    response = client.post("/order", json={
        "name": "Пицца Аррива средняя",
        "district": "Индустриальный"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    order_id = data['order_id']
    courier_id = data['courier_id']

    response = client.get(f"/order/{order_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['courier_id'] == courier_id
    assert data['status'] == 1

    response = client.post(f"/order/{order_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['message'] == 'OK'

    response = client.get(f"/order/{order_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['status'] == 2

    response = client.post(f"/order/{order_id}")
    assert response.status_code == 404, response.text


def test_create_courier_bad_request_body():
    response = client.post("/courier", json={})
    assert response.status_code == 422, response.text

    response = client.post("/courier", json={
        "name": "Courier 2",
        "districts": []
    })
    assert response.status_code == 422, response.text

    response = client.post("/courier", json={
        "name": "s34ricts"
    })
    assert response.status_code == 422, response.text

    response = client.post("/courier", json={
        "districts": []
    })
    assert response.status_code == 422, response.text


def test_get_courier_incorrect_id():
    response = client.get("/courier/fdasf23234")
    assert response.status_code == 422, response.text


def test_get_courier_not_found():
    response = client.get("/courier/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404, response.text


def test_create_order_bad_request_body():
    response = client.post("/order", json={})
    assert response.status_code == 422, response.text

    response = client.post("/order", json={
        "name": "",
        "district": ""
    })
    assert response.status_code == 422, response.text

    response = client.post("/order", json={
        "name": "name"
    })
    assert response.status_code == 422, response.text

    response = client.post("/order", json={
        "district": "district"
    })
    assert response.status_code == 422, response.text


def test_get_order_incorrect_id():
    response = client.get("/order/trtttwwww")
    assert response.status_code == 422, response.text


def test_get_order_not_found():
    response = client.get("/order/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404, response.text


def test_complete_order_incorrect_id():
    response = client.post("/order/qwerty123")
    assert response.status_code == 422, response.text


def test_complete_order_not_found():
    response = client.post("/order/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404, response.text
