#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python manage.py shell << EOF
from django.contrib.auth import get_user_model

User = get_user_model()

user, _ = User.objects.get_or_create(username="admin")

user.email = "admin@example.com"
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.set_password("AdminPassword123")
user.save()

print("Admin user created/updated")
EOF
