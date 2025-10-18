from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review,
        name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/',
        views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/',
        views.delete_review, name='movies.delete_review'),
    path('<int:id>/review/<int:review_id>/report/',
        views.report_review, name='movies.report_review'),
    path('map/', views.local_popularity_map, name='movies.local_map'),
    path('map/data/', views.map_data, name='movies.map_data'),
    path('map/region/<str:region_code>/', views.region_top, name='movies.region_top'),
    path('<int:id>/rate/', views.rate_movie, name='movies.rate'),
]
