web: python manage.py fix_migrations && python manage.py migrate && gunicorn CarRentalService.wsgi:application --bind 0.0.0.0:$PORT
