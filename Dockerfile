
FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN pip list

COPY . /app/

# EXPOSE 8000

# CMD ["gunicorn", "app:app"]