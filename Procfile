web: python manage.py migrate && python manage.py createcachetable && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
