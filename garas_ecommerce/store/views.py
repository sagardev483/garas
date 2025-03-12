from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Product, CartItem, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def home_view(request):
    featured_categories = Category.objects.filter(featured=True)
    latest_products = Product.objects.all().order_by('-created_at')[:8]
    context = {
        'featured_categories': featured_categories,
        'latest_products': latest_products,
    }
    return render(request, 'store/home.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)

    # Basic filters (price, stock, sale)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        products = products.filter(stock__gt=0)

    on_sale = request.GET.get('on_sale')
    if on_sale == '1':
        products = products.filter(is_sale=True)

    context = {
        'category': category,
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock': in_stock,
        'on_sale': on_sale,
    }
    return render(request, 'store/category_detail.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {'product': product}
    return render(request, 'store/product_detail.html', context)


def cart_view(request):
    session_key = get_session_key(request)
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart_items = CartItem.objects.filter(session_key=session_key, user__isnull=True)
    total = sum(item.get_subtotal() for item in cart_items)
    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'store/cart.html', context)


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    session_key = get_session_key(request)
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
        )
    else:
        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            product=product,
            user=None
        )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart')
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to homepage after signup
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    messages.info(request, f"Removed {cart_item.product.name} from cart.")
    return redirect('cart')


@login_required
def checkout_view(request):
    session_key = get_session_key(request)
    cart_items = CartItem.objects.filter(
        Q(user=request.user) | Q(session_key=session_key, user__isnull=True)
    )
    if request.method == 'POST':
        order = Order.objects.create(user=request.user)
        total_amount = 0
        for item in cart_items:
            line_total = item.get_subtotal()
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_display_price()
            )
            total_amount += line_total
        order.total_amount = total_amount
        order.is_paid = False  # Adjust if integrating real payment
        order.save()
        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect('order_complete', order_id=order.id)
    total = sum(item.get_subtotal() for item in cart_items)
    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'store/checkout.html', context)


@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'store/order_complete.html', context)
