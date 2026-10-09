from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.index, name='index'),
    path('noticia/<int:pk>/', views.article_detail, name='article_detail'),
    path('categoria/<slug:slug>/', views.category_list, name='category_list'),
]
