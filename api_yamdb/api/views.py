from api.filters import TitleFilter
from api.permission import AdminOrReadOnly, IsOwnerOrAdminOrModerator
from api.serializers import (CategorySerializer, CommentSerializers,
                             GenreSerializer, ReadTitleSerializer,
                             ReviewSerializer, WriteTitleSerializer)
from api.viewsets import CategoryGenreViewSet
from django.db.models import Avg
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title


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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadTitleSerializer
        return WriteTitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Представление для комментариев."""
    model = Comment
    serializer_class = CommentSerializers
    permission_classes = (IsOwnerOrAdminOrModerator,)

    def get_comment(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def perform_create(self, serializer):
        comment = self.get_comment()
        serializer.save(author=self.request.user, review=comment)

    def get_queryset(self):
        comment = self.get_comment()
        return comment.comments.all()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление для отзывов и оценки."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrModerator,)

    def perform_create(self, serializer):
        title_id = self.kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        author = self.request.user
        existing_review = Review.objects.filter(
            title=title, author=author
        ).first()
        if existing_review:
            raise ValidationError('Вы уже оставляли отзыв этому произведению')
        serializer.save(title=title, author=author)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
