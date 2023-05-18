#  импортируйте в код всё необходимое
from django.urls import include, path
from rest_framework import routers

from .views import PostViewSet

app_name = 'api_posts'

router = routers.DefaultRouter()
router.register('api/v1/posts', PostViewSet)


urlpatterns = [
    path('', include(router.urls)),
]