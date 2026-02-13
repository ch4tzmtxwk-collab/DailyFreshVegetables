from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    local_name = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class SiteSettings(models.Model):
    whatsapp_enabled = models.BooleanField(default=True)
    country_code = models.CharField(max_length=5, default="91")

    def __str__(self):
        return "Site Settings"

class Order(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50) # e.g. "1 kg" or just "1"
    price_at_time = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
