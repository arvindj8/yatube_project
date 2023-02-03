from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView, View

from posts.forms import CommentForm
from posts.models import Comment, Follow, Group, Like, Post, User


class IndexListView(ListView):
    """Главная страница с функцией поиска постов по ключевому слову"""
    model = Post
    template_name = 'posts/index.html'
    paginate_by = settings.AMOUNT_POSTS

    def get_queryset(self):
        keyword = self.request.GET.get("q", None)
        if keyword:
            page_obj = Post.objects.select_related('author', 'group').filter(
                text__contains=keyword)
        else:
            page_obj = Post.objects.select_related('author', 'group')
        return page_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Последние обновления на сайте'
        return context


class GroupPostsListView(ListView):
    """Страница постов привязанная к конкретной группе"""
    model = Post
    template_name = 'posts/group_list.html'
    paginate_by = settings.AMOUNT_POSTS

    def get_queryset(self):
        group = get_object_or_404(Group, slug=self.kwargs.get('slug'))
        queryset = group.posts.select_related('author')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(
            Group, slug=self.kwargs.get('slug')
        )
        return context


class ProfileListView(ListView):
    """Карточка профайла автора с возможностью подписаться или отписаться"""
    model = Post
    template_name = 'posts/profile.html'
    paginate_by = settings.AMOUNT_POSTS

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        queryset = author.posts.select_related('group')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = get_object_or_404(
            User, username=self.kwargs.get('username'))
        context['posts'] = self.get_queryset()
        if self.request.user.is_authenticated:
            context['following'] = context['author'].following.select_related(
                'user'
            )
        else:
            context['following'] = False
        return context


class PostDetailView(FormView):
    """Карточка поста с формой комментария и лайками"""
    form_class = CommentForm
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(
            Post, id=self.kwargs.get('post_id'))
        context['posts'] = context['post'].author.posts.count()
        context['comments'] = context['post'].comments.select_related('author')
        if self.request.user.is_authenticated:
            context['likes'] = context['post'].likes.select_related('user')
            context['like_record'] = Like.objects.filter(
                post_id=self.kwargs.get('post_id'), user=self.request.user)
        return context


class PostCreateView(CreateView):
    """Создание поста"""
    model = Post
    template_name = 'posts/create_post.html'
    fields = ['text', 'group', 'image']

    def get_success_url(self):
        return reverse_lazy('posts:profile', args=[self.object.author])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditView(UpdateView):
    """Редактирование поста"""
    model = Post
    template_name = 'posts/create_post.html'
    fields = ['text', 'group', 'image']
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        if self.request.user != post.author:
            return redirect('posts:post_detail', self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class CommentCreateView(CreateView):
    """Создание комментарий"""
    model = Comment
    fields = ['text']

    def get_success_url(self):
        return reverse_lazy(
            'posts:post_detail', kwargs={'post_id': self.kwargs['post_id']})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post,
                                               id=self.kwargs.get('post_id'))
        return super().form_valid(form)


class FollowIndexListView(ListView):
    """Отображение постов любимых авторов"""
    model = Post
    template_name = 'posts/follow.html'
    paginate_by = settings.AMOUNT_POSTS

    def get_queryset(self):
        future_posts = Post.objects.filter(
            author__following__user=self.request.user)
        return future_posts


class ProfileFollowView(View):
    # Подписаться на автора
    def get(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        if request.user != author:
            Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', author.username)


class ProfileUnfollowView(View):
    """Отписка от автора"""

    def get(self, request, *args, **kwargs):
        author = get_object_or_404(User, username=self.kwargs.get('username'))
        unfollowing = Follow.objects.filter(user=request.user, author=author)
        unfollowing.delete()
        return redirect('posts:profile', author.username)


class LikePostView(ListView):
    """Лайк"""

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        if self.request.user.is_authenticated:
            Like.objects.get_or_create(post_id=post.id,
                                       user=request.user,
                                       like=1)
        return redirect('posts:post_detail', post.id)


class UnlikePost(ListView):
    """Дизлайк"""

    def get(self, request, *args, **kwargs):
        record_like = Like.objects.filter(
            post_id=self.kwargs.get('post_id'), user=request.user)
        record_like.delete()
        return redirect('posts:post_detail', self.kwargs.get('post_id'))
