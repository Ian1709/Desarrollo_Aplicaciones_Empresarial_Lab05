"""Rutas públicas de la app `movies` (Paso 10)."""

from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('pelicula/<int:pk>/', views.movie_detail, name='movie_detail'),
]