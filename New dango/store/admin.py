from django.contrib import admin
from .models import Product, Order, OrderItem, SiteSettings

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'local_name', 'price', 'unit']
    search_fields = ['name', 'local_name']
    list_filter = ['unit']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'local_name')
        }),
        ('Pricing & Unit', {
            'fields': ('price', 'unit')
        }),
        ('Media & Description', {
            'fields': ('image', 'description')
        }),
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone_number', 'total_amount', 'created_at']
    search_fields = ['full_name', 'phone_number', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'id']
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'created_at')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'phone_number', 'email', 'address')
        }),
        ('Payment', {
            'fields': ('total_amount',)
        }),
    )

    def has_add_permission(self, request):
        return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price_at_time']
    search_fields = ['order__id', 'product__name']
    list_filter = ['order__created_at']
    readonly_fields = ['order', 'product', 'quantity', 'price_at_time']

    def has_add_permission(self, request):
        return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_enabled', 'country_code']
    fieldsets = (
        ('WhatsApp Configuration', {
            'fields': ('whatsapp_enabled', 'country_code')
        }),
    )
