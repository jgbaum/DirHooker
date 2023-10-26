FROM python:3.12-slim-bullseye

RUN apt -y update

RUN apt -y install curl inotify-tools

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .