import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

from django.contrib.auth.models import User

username = "Omkar"
password = "omkar"

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        print(f"Updated existing user '{username}' with admin privileges.")
    else:
        User.objects.create_superuser(username=username, password=password, email="")
        print(f"Created new superuser '{username}'.")

except Exception as e:
    print(f"Error: {e}")
