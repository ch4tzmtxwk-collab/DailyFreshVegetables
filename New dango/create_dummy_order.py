
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from store.models import Product, Order, OrderItem
# Create dummy products if none
if not Product.objects.exists():
    Product.objects.create(name="Tomato", price=40, unit="kg")
    Product.objects.create(name="Onion", price=30, unit="kg")

products = list(Product.objects.all())

# Create a dummy order
order = Order.objects.create(
    full_name="Admin Test",
    phone_number="9876543210",
    email="admin@example.com",
    address="123 Admin Lane, Test City",
    total_amount=150.00
)

# Add items
if products:
    p1 = products[0]
    OrderItem.objects.create(order=order, product=p1, quantity="2 kg", price_at_time=p1.price)
    
print(f"Created Order #{order.id}: {order}")
