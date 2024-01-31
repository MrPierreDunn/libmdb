from django.urls import include, path
from rest_framework import routers

from users.v1.views import send_confirmation_code, send_token, UserViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet)

urlpatterns = [
    path('v1/auth/signup/', send_confirmation_code),
    path('v1/auth/token/', send_token),
    path('v1/', include(router_v1.urls))
]
