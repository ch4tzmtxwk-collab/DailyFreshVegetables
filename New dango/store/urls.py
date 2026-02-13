from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('order/', views.create_order, name='create_order'),
    path('submit_order/', views.submit_order, name='submit_order'),
    path('store-admin/', views.store_admin, name='store_admin'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('add-product/', views.admin_add_product, name='admin_add_product'),
    path('edit-product/<int:pk>/', views.admin_edit_product, name='admin_edit_product'),
    path('delete-product/<int:pk>/', views.admin_delete_product, name='admin_delete_product'),
    path('order-bill/<int:order_id>/', views.order_bill, name='order_bill'),
    path('my-orders/', views.customer_orders, name='customer_orders'),
    path('api/customer-orders/', views.get_customer_orders_api, name='get_customer_orders_api'),
    path('store-admin/add-admin/', views.admin_add_admin, name='admin_add_admin'),
    path('store-admin/delete-admin/<int:user_id>/', views.admin_delete_admin, name='admin_delete_admin'),
]
