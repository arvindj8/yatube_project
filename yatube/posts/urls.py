from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (CommentCreateView, FollowIndexListView, GroupPostsListView,
                    IndexListView, LikePostView, PostCreateView,
                    PostDetailView, PostEditView, ProfileFollowView,
                    ProfileListView, ProfileUnfollowView, UnlikePost)

app_name = 'posts'

urlpatterns = [
    path('',
         cache_page(20, key_prefix='index_page')
         (IndexListView.as_view()),
         name='index'),

    path('group/<slug:slug>/',
         GroupPostsListView.as_view(),
         name='group_list'),

    path('profile/<str:username>/',
         ProfileListView.as_view(),
         name='profile'),

    path('create/',
         login_required(PostCreateView.as_view()),
         name='post_create'),

    path('posts/<int:post_id>/',
         PostDetailView.as_view(),
         name='post_detail'),

    path('posts/<int:post_id>/comment/',
         login_required(CommentCreateView.as_view()),
         name='add_comment'),

    path('posts/<int:post_id>/edit/',
         login_required(PostEditView.as_view()),
         name='post_edit'),

    path('follow/',
         login_required(FollowIndexListView.as_view()),
         name='follow_index'),

    path('profile/<str:username>/follow/',
         login_required(ProfileFollowView.as_view()),
         name='profile_follow'),

    path('profile/<str:username>/unfollow/',
         login_required(ProfileUnfollowView.as_view()),
         name='profile_unfollow'),

    path('posts/<int:post_id>/like/',
         login_required(LikePostView.as_view()),
         name='post_like'),

    path('posts/<int:post_id>/unlike/',
         login_required(UnlikePost.as_view()),
         name='post_unlike'),
]
