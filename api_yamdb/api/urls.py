from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet)
from api.views import UserViewSet, send_confirmation_code, send_token

app_name = 'api'

v1_router = routers.DefaultRouter()
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genres'
)
v1_router.register(
    'titles',
    TitleViewSet,
    basename='titles'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
v1_router.register(
    'users',
    UserViewSet,
    basename='users')

auth_urls = [
    path(
        'signup/',
        send_confirmation_code,
        name='signup'
    ),
    path(
        'token/',
        send_token,
        name='token'
    )
]


urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/', include(auth_urls)),
]
