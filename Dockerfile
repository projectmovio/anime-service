FROM python:3.7-alpine3.8

EXPOSE 8085

ADD requirements.txt /usr/local/src/anime-service/requirements.txt
RUN pip install -r /usr/local/src/anime-service/requirements.txt

ADD /service /usr/local/src/anime-service/service
ADD /config /usr/local/src/anime-service/config

WORKDIR /usr/local/src/anime-service
CMD ["python", "run_flask.py"]
