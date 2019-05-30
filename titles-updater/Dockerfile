FROM python:3.7-alpine3.8

RUN apk update
RUN apk add bash

WORKDIR /usr/local/src/titles-updater

ADD ./titles-updater/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

ADD ./titles-updater/titles_updater.py ./titles_updater.py
ADD ./config ./config

ENTRYPOINT ["python", "titles_updater.py"]