#!/usr/bin/env bash

mkdir /var/cache/anime_service
chown nginx:nginx /var/cache/anime_service

nginx
uwsgi --ini uwsgi.ini
