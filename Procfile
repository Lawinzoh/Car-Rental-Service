web: python manage.py reset_migrations && python manage.py collectstatic --noinput && gunicorn CarRentalService.wsgi:application --bind 0.0.0.0:$PORT
