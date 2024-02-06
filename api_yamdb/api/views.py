from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from api.filters import TitleFilter
from api.permission import AdminOrReadOnly, IsOwnerOrAdminOrModerator
from api.serializers import (CategorySerializer, CommentSerializers,
                             GenreSerializer, ReadTitleSerializer,
                             ReviewSerializer, WriteTitleSerializer)
from api.viewsets import CategoryGenreViewSet
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
