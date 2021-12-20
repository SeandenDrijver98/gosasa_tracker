release: python manage.py migrate --noinput
release: python manage.py collectstatic
web: gunicorn gosasa_tracker.wsgi