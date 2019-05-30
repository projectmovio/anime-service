FROM python:3.7-alpine3.8

RUN apk update
RUN apk add bash

WORKDIR /usr/local/src

ADD ./titles-updater/requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

ADD ./titles-updater/run.sh ./titles-updater/run.sh
ADD ./titles-updater/titles_updater.py ./titles-updater/titles_updater.py
ADD ./config ./config

ENTRYPOINT ["bash", ",/titles-updater/run.sh"]