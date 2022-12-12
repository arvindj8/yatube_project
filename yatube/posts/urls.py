from django.urls import path, include
from . import views

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),

    # Страница, на которой будут посты, отфильтрованные по группам.
    # Ждем переменную типа slug
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
]
