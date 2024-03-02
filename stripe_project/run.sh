#!/bin/sh
# run.sh

python manage.py migrate

python manage.py collectstatic --noinput

cp -r /app/collected_static/. /backend_static/

gunicorn stripe_project.wsgi --bind=0.0.0.0:8000
