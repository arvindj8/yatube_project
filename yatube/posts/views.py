from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse('Главная страницы')


def group_posts(request, slug):
    return HttpResponse('Страница, на которой будут посты, отфильтрованные по группам')

