FROM python:3.7

EXPOSE 8085

ADD requirements.txt /usr/local/src/anime-service/requirements.txt
RUN pip install -r /usr/local/src/anime-service/requirements.txt

ADD /service /usr/local/src/anime-service/service
ADD /cache /usr/local/src/anime-service/cache
ADD run_flask.py /usr/local/src/anime-service/run_flask.py

ADD config.json /usr/local/src/anime-service/config.json

WORKDIR /usr/local/src/anime-service
CMD ["python", "run_flask.py"]
