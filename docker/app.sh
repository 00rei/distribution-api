#!/bin/bash

alembic upgrade head

pytest -s -v -p no:warnings

uvicorn src.main:app --host 0.0.0.0 --port 8000