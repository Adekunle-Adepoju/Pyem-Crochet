from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Order, OrderItem


def home(request):
    products = Product.objects.all()[:3]
    return render(request, 'index.html', {'products': products})


def shop(request):
    category = request.GET.get('category')
    if category:
        all_products = Product.objects.filter(category=category)
    else:
        all_products = Product.objects.all()
    paginator = Paginator(all_products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'shop.html', {
        'products': products,
        'category': category,
    })


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = None
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back, ' + user.first_name + '!')
            return redirect('index')
        else:
            messages.error(request, 'Incorrect email or password. Please try again.')
    return render(request, 'signin.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists. Please sign in instead.')
            return render(request, 'register.html')
        if User.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists. Please sign in instead.')
            return render(request, 'register.html')
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, 'Welcome to Pyem Stitches, ' + first_name + '!')
            return redirect('index')
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'register.html')
    return render(request, 'register.html')


def signout(request):
    logout(request)
    return redirect('index')


def cart(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to sign in to view your cart.')
        return redirect('signin')
    cart_data = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            price = product.get_price()
            subtotal = price * quantity
            cart_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
                'price': price,
            })
        except Product.DoesNotExist:
            pass
    grand_total = cart_total + 1500
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'grand_total': grand_total,
    })


def add_to_cart(request, product_id):
    cart_data = request.session.get('cart', {})
    key = str(product_id)
    if key in cart_data:
        cart_data[key] += 1
    else:
        cart_data[key] = 1
    request.session['cart'] = cart_data
    messages.success(request, 'Item added to cart!')
    return redirect('shop')


def increase_cart(request, product_id):
    cart_data = request.session.get('cart', {})
    key = str(product_id)
    if key in cart_data:
        cart_data[key] += 1
    request.session['cart'] = cart_data
    return redirect('cart')


def decrease_cart(request, product_id):
    cart_data = request.session.get('cart', {})
    key = str(product_id)
    if key in cart_data:
        cart_data[key] -= 1
        if cart_data[key] <= 0:
            del cart_data[key]
    request.session['cart'] = cart_data
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart_data = request.session.get('cart', {})
    key = str(product_id)
    if key in cart_data:
        del cart_data[key]
    request.session['cart'] = cart_data
    return redirect('cart')


def order(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to sign in before placing an order.')
        return redirect('signin')

    if request.method == 'POST':
        cart_data = request.session.get('cart', {})

        if not cart_data:
            messages.error(request, 'Your cart is empty. Please add items before ordering.')
            return redirect('shop')

        new_order = Order.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            state=request.POST.get('state'),
            gender=request.POST.get('gender'),
            chest=request.POST.get('chest'),
            waist=request.POST.get('waist'),
            hip=request.POST.get('hip'),
            shoulder=request.POST.get('shoulder'),
            sleeve=request.POST.get('sleeve'),
            top_length=request.POST.get('top_length'),
            trouser_length=request.POST.get('trouser_length'),
            thigh=request.POST.get('thigh'),
            notes=request.POST.get('notes'),
            colour=request.POST.get('colour'),
            colour_notes=request.POST.get('colour_notes'),
            status='Pending',
            payment_status='Unpaid',
        )

        cart_total = 0
        order_items_text = ''
        for product_id, quantity in cart_data.items():
            try:
                product = Product.objects.get(id=product_id)
                price = product.get_price()
                OrderItem.objects.create(
                    order=new_order,
                    product=product,
                    quantity=quantity,
                    price=price,
                )
                cart_total += price * quantity
                order_items_text += f'- {product.name} x{quantity} = ₦{price * quantity}\n'
            except Product.DoesNotExist:
                pass

        new_order.total = cart_total + 1500
        new_order.save()

        try:
            send_mail(
                subject=f'New Order #{new_order.id} from {new_order.full_name}',
                message=f'''
You have a new order on Pyem Stitches!

ORDER DETAILS
--------------
Order ID: #{new_order.id}
Customer: {new_order.full_name}
Phone: {new_order.phone}
Email: {new_order.email}
State: {new_order.state}
Address: {new_order.address}

ITEMS ORDERED
--------------
{order_items_text}
Delivery: ₦1,500
Total: ₦{new_order.total}

MEASUREMENTS
--------------
Chest: {new_order.chest} inches
Waist: {new_order.waist} inches
Hip: {new_order.hip} inches
Shoulder: {new_order.shoulder} inches
Sleeve: {new_order.sleeve} inches
Top Length: {new_order.top_length} inches
Trouser/Skirt Length: {new_order.trouser_length} inches
Thigh: {new_order.thigh} inches

COLOUR PREFERENCE
--------------
Colour: {new_order.colour}
Notes: {new_order.colour_notes}

View full order at: http://127.0.0.1:8000/admin-panel/order/{new_order.id}/
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['Seunopeyemi1708@gmail.com'],
                fail_silently=True,
            )
        except:
            pass

        request.session['cart'] = {}
        request.session.modified = True
        return redirect('payment', order_id=new_order.id)

    cart_data = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.get_price() * quantity
            cart_total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            pass
    grand_total = cart_total + 1500
    return render(request, 'order.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'grand_total': grand_total,
    })


def payment(request, order_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    order = get_object_or_404(Order, id=order_id)
    amount_to_pay = order.total / 2
    return render(request, 'payment.html', {
        'order': order,
        'amount_to_pay': amount_to_pay,
    })


def confirm_payment(request, order_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        transfer_reference = request.POST.get('transfer_reference')
        receipt = request.FILES.get('receipt')
        order.transfer_reference = transfer_reference
        order.payment_status = 'Awaiting Confirmation'
        if receipt:
            order.receipt = receipt
        order.save()
        try:
            send_mail(
                subject=f'Payment Receipt Submitted – Order #{order.id}',
                message=f'''
A customer has submitted payment for Order #{order.id}.

Customer: {order.full_name}
Phone: {order.phone}
Email: {order.email}
Amount Due: ₦{order.total / 2}
Transfer Reference: {transfer_reference}

Please confirm the payment in the admin panel:
http://ade22.pythonanywhere.com/admin-panel/order/{order.id}/
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['Seunopeyemi1708@gmail.com'],
                fail_silently=True,
            )
        except:
            pass
        messages.success(request, 'Payment details submitted! We will confirm within a few hours.')
        return redirect('success')
    return redirect('payment', order_id=order.id)


def success(request):
    return render(request, 'success.html')


def profile(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    return render(request, 'profile.html', {'user': request.user})


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


def delete_account(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('index')
    return render(request, 'delete_account.html')


def admin_panel(request):
    if not request.user.is_staff:
        return redirect('index')
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_panel.html', {
        'products': products,
        'orders': orders,
    })


def add_product(request):
    if not request.user.is_staff:
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        category = request.POST.get('category')
        gender = request.POST.get('gender')
        badge = request.POST.get('badge')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if discount_price and discount_price.strip() != '':
            discount_price = discount_price.strip()
        else:
            discount_price = None
        Product.objects.create(
            name=name,
            price=price,
            discount_price=discount_price,
            category=category,
            gender=gender,
            badge=badge,
            description=description,
            image=image,
        )
        messages.success(request, '"' + name + '" has been added to the shop!')
        return redirect('admin_panel')
    return redirect('admin_panel')


def edit_product(request, product_id):
    if not request.user.is_staff:
        return redirect('index')
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        discount_price = request.POST.get('discount_price')
        product.discount_price = discount_price if discount_price and discount_price.strip() != '' else None
        product.category = request.POST.get('category')
        product.gender = request.POST.get('gender')
        product.badge = request.POST.get('badge')
        product.description = request.POST.get('description')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        messages.success(request, '"' + product.name + '" has been updated successfully!')
        return redirect('admin_panel')
    return render(request, 'edit_product.html', {'product': product})


def delete_product(request, product_id):
    if not request.user.is_staff:
        return redirect('index')
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('admin_panel')


def order_detail(request, order_id):
    if not request.user.is_staff:
        return redirect('index')
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    if request.method == 'POST':
        payment_action = request.POST.get('payment_action')
        if payment_action == 'confirm':
            order.payment_status = 'Half Paid'
            order.amount_paid = order.total / 2
            order.save()
            try:
                send_mail(
                    subject=f'Payment Confirmed – Order #{order.id}',
                    message=f'''
Hi {order.full_name},

Your payment of ₦{order.total / 2} for Order #{order.id} has been confirmed!

We will now begin stitching your outfit. You will be notified once it is ready for delivery.

Remaining balance of ₦{order.total / 2} will be collected on delivery.

Thank you for choosing Pyem Stitches!
📞 09125072582
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    fail_silently=True,
                )
            except:
                pass
            messages.success(request, 'Payment confirmed! Customer has been notified.')
            return redirect('order_detail', order_id=order.id)

        old_status = order.status
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

        if old_status != new_status:
            try:
                if new_status == 'Stitching':
                    subject = f'Your Order #{order.id} is being stitched!'
                    message = f'''
Hi {order.full_name},

Great news! Your order #{order.id} from Pyem Stitches is now being stitched.

Our tailor has started working on your outfit and it will be ready soon.

If you have any questions contact us:
📞 09125072582
✉️ Seunopeyemi1708@gmail.com

Thank you for choosing Pyem Stitches!
                    '''
                elif new_status == 'Delivered':
                    subject = f'Your Order #{order.id} has been delivered!'
                    message = f'''
Hi {order.full_name},

Your order #{order.id} from Pyem Stitches has been delivered!

We hope you love your new outfit. Thank you for choosing Pyem Stitches.

Please remember to pay the remaining balance of ₦{order.total / 2} on delivery.

If you have any issues contact us:
📞 09125072582
✉️ Seunopeyemi1708@gmail.com

Thank you for choosing Pyem Stitches!
                    '''
                elif new_status == 'Cancelled':
                    subject = f'Your Order #{order.id} has been cancelled'
                    message = f'''
Hi {order.full_name},

Unfortunately your order #{order.id} from Pyem Stitches has been cancelled.

If you think this is a mistake or need more information please contact us:
📞 09125072582
✉️ Seunopeyemi1708@gmail.com

We are sorry for any inconvenience caused.
                    '''
                else:
                    subject = None
                    message = None

                if subject and message and order.email:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email],
                        fail_silently=True,
                    )
            except:
                pass

        messages.success(request, 'Order status updated to ' + new_status + '.')
        return redirect('order_detail', order_id=order.id)

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
    })