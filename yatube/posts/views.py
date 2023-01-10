from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from posts.models import Post, Group, User
from posts.forms import PostForm
from core.my_functions.pagination import pagination


def index(request):
    title = 'Последние обновления на сайте'
    posts = Post.objects.select_related('author', 'group')

    context = {
        'title': title,
        'page_obj': pagination(request, posts, settings.AMOUNT_POSTS)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')

    context = {
        'group': group,
        'page_obj': pagination(request, posts, settings.AMOUNT_POSTS)
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    context = {
        'page_obj': pagination(request, posts, settings.AMOUNT_POSTS),
        'posts': posts,
        'author': author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    context = {
        'post': post,
        'posts': post.author.posts.count()
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', context={'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid() and request.user == post.author:
        form.save()
        return redirect('posts:post_detail', post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)
