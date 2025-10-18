from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from cart.models import Item
from django.contrib.auth.decorators import login_required
from .forms import RatingForm               # make sure RatingForm exists

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie =  Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '': 
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie__id=id)
    review.reported = True
    review.save()
    return redirect('movies.show', id=id)

# Map a few known region codes to marker coordinates
REGION_COORDS = {
    "GA-Atlanta": {"lat": 33.7490, "lng": -84.3880},
    "NY-NYC": {"lat": 40.7128, "lng": -74.0060},
    "CA-SF": {"lat": 37.7749, "lng": -122.4194},
    "WA-Seattle": {"lat": 47.6062, "lng": -122.3321},
    "TX-Austin": {"lat": 30.2672, "lng": -97.7431},
}

@login_required
def local_popularity_map(request):
    template_data = {"title": "Local Popularity Map"}
    return render(request, 'movies/local_popularity_map.html', {'template_data': template_data})

def map_data(request):
    # Aggregate per region_code and movie name
    items = (
        Item.objects.select_related('order', 'movie')
        .values('order__region_code', 'movie__name')
        .annotate(count=Sum('quantity'))
    )
    by_region = {}
    for row in items:
        rc = row['order__region_code'] or 'Unknown'
        by_region.setdefault(rc, [])
        by_region[rc].append((row['movie__name'], row['count']))

    payload = []
    for rc, pairs in by_region.items():
        pairs.sort(key=lambda x: x[1], reverse=True)
        coord = REGION_COORDS.get(rc)
        payload.append({
            "region_code": rc,
            "coords": coord,
            "top_movies": [{"title": t, "count": int(c)} for t, c in pairs[:5]],
            "total_purchases": int(sum(c for _, c in pairs)),
        })
    return JsonResponse({"regions": payload})

def region_top(request, region_code):
    # Top titles in the selected region
    region_rows = (
        Item.objects.select_related('order', 'movie')
        .filter(order__region_code=region_code)
        .values('movie__name')
        .annotate(count=Sum('quantity'))
        .order_by('-count')[:10]
    )
    top_list = [{"title": r['movie__name'], "count": int(r['count'])} for r in region_rows]

    # Current user's recent purchases (for comparison)
    my_recent = []
    if request.user.is_authenticated:
        my_rows = (
            Item.objects.select_related('order', 'movie')
            .filter(order__user=request.user)
            .values('movie__name')
            .annotate(count=Sum('quantity'))
            .order_by('-count')[:10]
        )
        my_recent = [{"title": r['movie__name'], "count": int(r['count'])} for r in my_rows]

    return JsonResponse({"region_code": region_code, "top_movies": top_list, "my_recent": my_recent})

@login_required
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)

    try:
        rating = Rating.objects.get(user=request.user, movie=movie)
    except Rating.DoesNotExist:
        rating = None

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.user = request.user
            new_rating.movie = movie
            new_rating.save()
            return redirect('movies.show', id=id)
    else:
        form = RatingForm(instance=rating)

    template_data = {
        'title': f'Rate {movie.name}',
        'movie': movie,
        'form': form,
        'average_rating': movie.average_rating(),
    }

    return render(request, 'movies/rate_movie.html', {'template_data': template_data})
