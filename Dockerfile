FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /memes/
WORKDIR /memes/

RUN pip install -r requirements.txt --no-cache-dir
