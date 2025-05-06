FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY . /app/

RUN poetry install --no-root

ENTRYPOINT poetry run uvicorn src.main:app --workers 2 --host 0.0.0.0 --port 8000
