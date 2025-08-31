#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
if not User.objects.filter(username='user').exists(): \
    User.objects.create_superuser('user','user@example.com','user12345')" | python manage.py shell
