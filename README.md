# REST API сервис для распределения заказов по курьерам

## Инструкция по развертыванию.

1. Скачайте проект:

```
git clone https://github.com/00rei/distribution-api.git
```

2. Перейдите в корневую папку проекта:

```
cd distribution-api
```

3. Выполните команду:
``` 
docker compose build
```

4. Когда команда будет выполнена, выполните следующую команду:
```
docker compose up
```

Во время выполнения последней команды можно будет увидеть сообщения о резульате выполнения тестов и запуске сервера Uvicorn.

Когда сервер будет запущен, перейдите по адресу http://localhost:7999/docs 