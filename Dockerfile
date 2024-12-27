FROM python:3.11.10-slim-bullseye as base_image

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



FROM base_image as prod_image

COPY . .



FROM base_image as dev_image

COPY requirements.dev.txt .

RUN pip install --no-cache-dir -r requirements.dev.txt

COPY . .