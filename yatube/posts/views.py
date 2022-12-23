from django.shortcuts import render, get_object_or_404
from posts.models import Post, Group
from django.conf import settings


def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()[:settings.AMOUNT_POSTS]
    context = {
        'title': title,
        'posts': posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)[:settings.AMOUNT_POSTS]
    title = f'Записи сообщества {group.title}'
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)
