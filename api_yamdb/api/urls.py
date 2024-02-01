from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet, UsersViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
router.register(
    'users',
    UsersViewSet,
    basename='users'
)


urlpatterns = [
    path('v1/', include(router.urls)),
]
