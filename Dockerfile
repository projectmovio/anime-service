FROM python:3.7-alpine3.8

EXPOSE 8085

RUN apk add --no-cache nginx uwsgi gcc libc-dev linux-headers bash
RUN pip install uwsgi

ADD nginx.conf /etc/nginx/conf.d
RUN mkdir /run/nginx

WORKDIR /usr/local/src

ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ADD ./service ./service
ADD ./config ./config
ADD ./uwsgi.ini ./
ADD ./start.sh ./

ADD ./cache/titles /var/cache/anime_service/titles

CMD ["bash", "start.sh"]
