from django.urls import include, path

app_name = 'users'

urlpatterns = [
    path('', include('users.v1.urls')),
]
