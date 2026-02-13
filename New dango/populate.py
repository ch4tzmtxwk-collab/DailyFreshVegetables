import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from store.models import Product

products = [
    {
        'name': 'Farmers Tomato',
        'local_name': 'टमाटर',
        'price': 40,
        'unit': 'kg',
    },
    {
        'name': 'Red Onion',
        'local_name': 'प्याज',
        'price': 30,
        'unit': 'kg',
    },
    {
        'name': 'Fresh Potato',
        'local_name': 'आलू',
        'price': 20,
        'unit': 'kg',
    },
    {
        'name': 'Spinach (Palak)',
        'local_name': 'पालक',
        'price': 15,
        'unit': 'bunch',
    },
]

for p_data in products:
    Product.objects.get_or_create(
        name=p_data['name'],
        defaults=p_data
    )

print("Products added successfully!")
