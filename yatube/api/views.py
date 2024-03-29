from rest_framework import generics, viewsets
from posts.models import Post
from posts.serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


