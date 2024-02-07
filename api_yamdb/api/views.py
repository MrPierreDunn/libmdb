from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permission import AdminOrReadOnly, IsAdmin, IsOwnerOrAdminOrModerator
from api.serializers import (CategorySerializer, CommentSerializers,
                             MeSerializer, GenreSerializer,
                             ReadTitleSerializer, ReviewSerializer,
                             TokenSerializer, UserCreateSerializer,
                             UserSerializer, WriteTitleSerializer)
from api.viewsets import CategoryGenreViewSet
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects
        .select_related('category')
        .prefetch_related('genre')
        .annotate(rating=Avg('reviews__score'))
    )
    permission_classes = (AdminOrReadOnly, )
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete',)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadTitleSerializer
        return WriteTitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для комментариев."""
    model = Comment
    queryset = Comment.objects.all()
    serializer_class = CommentSerializers
    permission_classes = (IsOwnerOrAdminOrModerator,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        review_id = self.kwargs['review_id']
        title_id = self.kwargs['title_id']
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        return review

    def perform_create(self, serializer):
        comment = self.get_review()
        serializer.save(author=self.request.user, review=comment)

    def get_queryset(self):
        return self.get_review().comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление для отзывов и оценки."""
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrModerator,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        return title

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user
        serializer.save(title=title, author=author)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    """Вью функция для получения кода подтверждения."""

    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.validated_data, status=status.HTTP_200_OK)



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


class UserViewSet(viewsets.ModelViewSet):
    """Вью-класс для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    permission_classes = (IsAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')
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
