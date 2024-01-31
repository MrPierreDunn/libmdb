from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from users.v1.permissions import IsAdmin
from users.models import User
from users.v1.serializers import (MeSerializer,
                                  TokenSerializer, UserSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """Отправляем код подтверждения."""
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    user, created = User.objects.get_or_create(
        email=email,
        username=username
    )
    if not created:
        user.email = email
        user.username = username
        user.save()
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Код подтверждения',
        f'{confirmation_code}',
        f'{settings.ADMIN_EMAIL}',
        [f'{email}'],
        fail_silently=False,
    )
    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token(request):
    """Отправляем токен при отправке кода подтверждения."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    confirmation_code = request.data.get('confirmation_code')
    refresh = RefreshToken.for_user(user)

    anwser = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    if default_token_generator.check_token(user, confirmation_code):
        AccessToken.for_user(user)
        user.save()
        return Response(anwser)
    return Response(
        {'Error': 'Проверьте код подтверждения'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    """Вью-класс для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def user(self, request):
        """Получение или обновление пользователя."""
        user = get_object_or_404(User, username=self.request.user)
        serializer = MeSerializer(self.request.user)

        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)
