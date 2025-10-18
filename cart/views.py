from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item

def index(request):
    cart = request.session.get('cart', {})
    # Support either string or int keys in the session cart
    movie_ids = list(cart.keys())
    if not movie_ids:
        movies_in_cart = []
        cart_total = 0
    else:
        # Coerce keys to ints for the query
        movie_ids_int = [int(mid) for mid in movie_ids]
        movies_in_cart = Movie.objects.filter(id__in=movie_ids_int)
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {
        'title': 'Cart',
        'movies_in_cart': movies_in_cart,
        'cart_total': cart_total,
    }
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    # Ensure movie exists
    get_object_or_404(Movie, id=id)

    # Normalize session cart
    cart = request.session.get('cart', {})

    # Normalize key to string to be consistent everywhere
    key = str(id)

    # Get quantity (default 1), sanitize to positive int
    qty_raw = request.POST.get('quantity', '1')
    try:
        qty = max(1, int(qty_raw))
    except ValueError:
        qty = 1

    cart[key] = qty
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart.index')

    # Collect movies in the cart (coerce ids to int for query)
    movie_ids_int = [int(mid) for mid in cart.keys()]
    movies_in_cart = Movie.objects.filter(id__in=movie_ids_int)

    # Compute total
    cart_total = calculate_cart_total(cart, movies_in_cart)

    # Create order and snapshot buyer region (if profile exists)
    order = Order()
    order.user = request.user
    # Snapshot region info from user profile if available
    if hasattr(request.user, 'profile'):
        order.city = request.user.profile.city
        order.state = request.user.profile.state
        order.region_code = request.user.profile.region_code
    order.total = cart_total
    order.save()

    # Create line items
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        # Cart keys are strings; guard against missing key
        item.quantity = int(cart.get(str(movie.id), 1))
        item.save()

    # Clear cart after purchase
    request.session['cart'] = {}

    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id,
    }
    return render(request, 'cart/purchase.html', {'template_data': template_data})
