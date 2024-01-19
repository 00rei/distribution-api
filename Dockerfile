FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD alembic upgrade head

RUN chmod +x docker/app.sh

#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]