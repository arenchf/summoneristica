from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search_sum', views.search_sum, name='search_sum'),
    path('search_match', views.search_match, name='search_match'),
]
