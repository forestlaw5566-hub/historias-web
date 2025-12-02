#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

gunicorn plataforma.wsgi:application --bind 0.0.0.0:$PORT
