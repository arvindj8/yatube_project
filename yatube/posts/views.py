from django.shortcuts import render, get_object_or_404
from posts.models import Post, Group


def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'title': title,
        'posts': posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    # В переменную group будут переданы объекты модели Group,
    # по полю slug
    group = get_object_or_404(Group, slug=slug)
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    title = f'Записи сообщества {group.title}'
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)

