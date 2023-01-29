from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.my_functions.pagination import pagination
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Follow


@cache_page(20, key_prefix='index_page')
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
    follow = author.following.select_related('user')
    if follow:
        following = True
    else:
        following = False

    context = {
        'page_obj': pagination(request, posts, settings.AMOUNT_POSTS),
        'posts': posts,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related('post')

    context = {
        'post': post,
        'posts': post.author.posts.count(),
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', context={'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
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


@login_required(login_url='/')
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(
        user=request.user).values_list('author', flat=True)
    posts = Post.objects.filter(author__in=following)
    context = {
        'page_obj': pagination(request, posts, settings.AMOUNT_POSTS)
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user != author:
        following = Follow.objects.create(user=request.user, author=author)
        following.save()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    unfollowing = Follow.objects.get(user=request.user, author=author)
    unfollowing.delete()
    return redirect('posts:profile', username=username)
