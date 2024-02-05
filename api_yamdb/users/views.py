from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from users.permission import IsAdmin
from users.serializers import (MeSerializer, TokenSerializer,
                               UserCreateSerializer, UserSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """Вью функция для получения кода подтверждения."""

    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    anwser = {'token': str(AccessToken.for_user(user))}
    return Response(anwser, status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """Вью-класс для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = MeSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
