from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Order, OrderItem
import json
from django.conf import settings
import urllib.request
import urllib.parse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
             return redirect('store_admin')
        # If logged in but not staff, maybe logout or show error? 
        # For now just let them see the login page again or error.
        # But wait, if they are authenticated they hit the redirect.
        # Let's just redirect to store_admin and let store_admin handle permission.

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('store_admin')
            else:
                error = "Access denied. Admin privileges required."
        else:
             error = "Invalid username or password."
    
    return render(request, 'store/admin_login.html', {'error': error})

from django.contrib.auth import logout
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def product_list(request):
    products = Product.objects.all().values()
    return JsonResponse(list(products), safe=False)

def create_order(request):
    if request.method == 'POST':
        # This handles standard form submission
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        # In a real app, we would process the cart items here.
        # Since the cart is frontend-only in the screenshots, 
        # we might need to rely on JS to send JSON data.
        return redirect('index')
    return redirect('index')

def submit_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_details = data.get('userDetails')
            cart_items = data.get('cartItems')
            total_amount = data.get('totalAmount')

            # Validation
            if not user_details:
                return JsonResponse({'status': 'error', 'message': 'Customer details missing'}, status=400)
            
            if not cart_items or len(cart_items) == 0:
                return JsonResponse({'status': 'error', 'message': 'Cart is empty'}, status=400)
            
            if not total_amount or float(total_amount) <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

            # Check individual fields
            missing = []
            if not user_details.get('fullName'): missing.append('Full Name')
            if not user_details.get('phoneNumber'): missing.append('Phone Number')
            if not user_details.get('address'): missing.append('Address')
            
            if missing:
                return JsonResponse({'status': 'error', 'message': f'Missing: {", ".join(missing)}'}, status=400)

            # Create Order
            order = Order.objects.create(
                full_name=user_details.get('fullName', ''),
                phone_number=user_details.get('phoneNumber', ''),
                email=user_details.get('email', ''),
                address=user_details.get('address', ''),
                total_amount=total_amount
            )

            # Create Order Items
            for item in cart_items:
                product_id = item.get('id')
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.get('quantity', '1'),
                            price_at_time=item.get('price', product.price)
                        )
                    except Product.DoesNotExist:
                        print(f"Product with ID {product_id} not found")
                        continue

            # Send Telegram Notification
            try:
                message_text = f"🔔 *New Order Received!* (Order #{order.id})\n\n"
                message_text += f"👤 *Customer:* {order.full_name}\n"
                message_text += f"📞 *Phone:* {order.phone_number}\n"
                message_text += f"📍 *Address:* {order.address}\n\n"
                message_text += "*🛒 Order Items:*\n"
                
                for item in cart_items:
                    prod_name = item.get('name', 'Unknown Product')
                    qty = item.get('quantity', '1')
                    message_text += f"- {prod_name} ({qty})\n"
                
                message_text += f"\n💰 *Total Amount:* ₹{order.total_amount}"

                # Verify Telegram credentials exist
                if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
                    print("⚠️ Telegram credentials not configured")
                else:
                    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
                    data_encoded = urllib.parse.urlencode({
                        'chat_id': settings.TELEGRAM_CHAT_ID, 
                        'text': message_text, 
                        'parse_mode': 'Markdown'
                    }).encode()
                    req = urllib.request.Request(url, data=data_encoded)
                    response = urllib.request.urlopen(req, timeout=10)
                    result = json.loads(response.read().decode())
                    if result.get('ok'):
                        print(f"TELEGRAM: Notification sent for Order #{order.id}")
                    else:
                        print(f"TELEGRAM ERROR: {result.get('description')}")
            except urllib.error.URLError as e:
                print(f"NETWORK ERROR (Telegram): {e.reason}")  # Log but don't fail the order
            except Exception as e:
                print(f"TELEGRAM EXCEPTION: {str(e)}")  # Log but don't fail the order

            return JsonResponse({'status': 'success', 'order_id': order.id})
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid request format'}, status=400)
        except Exception as e:
            print(f"Order Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Failed to place order: {str(e)}'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def store_admin(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    products = Product.objects.all()
    orders = Order.objects.prefetch_related('items__product').all().order_by('-created_at')
    
    admins = []
    if request.user.is_superuser:
        admins = User.objects.all()
        
    return render(request, 'store/store_admin.html', {
        'products': products, 
        'orders': orders,
        'admins': admins
    })

def admin_add_product(request):
    if not request.user.is_staff:
        return redirect('admin_login')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        local_name = request.POST.get('local_name')
        price = request.POST.get('price')
        unit = request.POST.get('unit')
        image = request.FILES.get('image')
        
        Product.objects.create(
            name=name,
            local_name=local_name,
            price=price,
            unit=unit,
            image=image
        )
        return redirect('store_admin')
    return redirect('store_admin')

def admin_edit_product(request, pk):
    if not request.user.is_staff:
        return redirect('admin_login')
        
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.local_name = request.POST.get('local_name')
        product.price = request.POST.get('price')
        product.unit = request.POST.get('unit')
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
            
        product.save()
        return redirect('store_admin')
    return redirect('store_admin')

def admin_delete_product(request, pk):
    if not request.user.is_staff:
        return redirect('admin_login')
        
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('store_admin')

def order_bill(request, order_id):
    if not request.user.is_staff:
        return redirect('admin_login')
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_bill.html', {'order': order})

def product_detail(request, pk):
    """Display detailed information about a single product"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

def customer_orders(request):
    """Display customer orders based on phone number"""
    orders = []
    phone_number = request.GET.get('phone', '')
    
    if phone_number:
        orders = Order.objects.filter(phone_number=phone_number).prefetch_related('items__product').order_by('-created_at')
    
    return render(request, 'store/customer_orders.html', {
        'orders': orders,
        'phone_number': phone_number
    })

def get_customer_orders_api(request):
    """API endpoint to get customer orders"""
    phone_number = request.GET.get('phone', '')
    
    if not phone_number:
        return JsonResponse({'status': 'error', 'message': 'Phone number required'}, status=400)
    
    orders = Order.objects.filter(phone_number=phone_number).prefetch_related('items__product').order_by('-created_at')
    
    orders_data = []
    for order in orders:
        items_data = []
        for item in order.items.all():
            items_data.append({
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.price_at_time)
            })
        
        orders_data.append({
            'id': order.id,
            'full_name': order.full_name,
            'phone_number': order.phone_number,
            'address': order.address,
            'total_amount': str(order.total_amount),
            'created_at': order.created_at.strftime('%d %b, %I:%M %p'),
            'items': items_data
        })
    
    return JsonResponse({'status': 'success', 'orders': orders_data})

def admin_add_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser privileges required.")
        return redirect('store_admin')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('store_admin')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        if role == 'superadmin':
            user.is_superuser = True
        # For simplicity, we can also use groups or other logic, but this is fine for now.
        user.save()
        messages.success(request, f"Admin '{username}' added successfully.")
        return redirect('store_admin')
    return redirect('store_admin')

def admin_delete_admin(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser privileges required.")
        return redirect('store_admin')
        
    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
        messages.error(request, "Cannot delete the last superuser.")
        return redirect('store_admin')
        
    if user == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('store_admin')
        
    username = user.username
    user.delete()
    messages.success(request, f"Admin '{username}' deleted successfully.")
    return redirect('store_admin')