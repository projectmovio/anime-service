FROM python:3.7

ADD /service /usr/local/src/anime-service/service
ADD /cache /usr/local/src/anime-service/cache
COPY run_flask.py /usr/local/src/anime-service/run_flask.py
COPY requirements.txt /usr/local/src/anime-service/requirements.txt
COPY config.json /usr/local/src/anime-service/config.json

WORKDIR /usr/local/src

EXPOSE 8085

RUN ["pip", "install", "-r", "requirements.txt"]
CMD ["python", "run_flask.py"]
