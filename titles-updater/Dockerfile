FROM python:3.7-alpine3.8

RUN apk update
RUN apk add bash

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD run.sh /run.sh
ADD titles_updater.py /titles-updater/titles_updater.py

ENTRYPOINT ["bash", "run.sh"]