#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py sincronizar_comedores_padron
python manage.py collectstatic --noinput

if [ $# -gt 0 ]; then
    exec "$@"
else
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
fi