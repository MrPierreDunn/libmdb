from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, GenreViewSet,
                       TitleViewSet)

from users.v1.views import (send_confirmation_code, send_token)

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


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', send_token),
]
