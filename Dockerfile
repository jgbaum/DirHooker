FROM python:3.12-slim-bullseye

RUN apt -y update

RUN apt -y install curl inotify-tools

WORKDIR /app

# copy requirements.txt first so we can do a pip install
# this helps make builds quicker
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python watch_dirs.py --runtime-config /config.yaml