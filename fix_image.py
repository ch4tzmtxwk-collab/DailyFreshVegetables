import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

from store.models import Product

try:
    p = Product.objects.get(name="Fresh Coriander")
    p.image_url = "" # Clear the bad URL so it falls back to the logo without a console error
    p.save()
    print("Successfully removed broken image URL for Fresh Coriander.")
except Product.DoesNotExist:
    print("Fresh Coriander product not found.")
except Exception as e:
    print(f"Error: {e}")
