from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.response import Response


from api.filters import TitleFilter
from api.permission import AdminAnonPermission, IsOwnerOrAdminOrModerator
from api.serializers import (CategorySerializer, CommentSerializers,
                             GenreSerializer, ReadTitleSerializer,
                             ReviewSerializer, WriteTitleSerializer)
from api.viewsets import ListCreateDelViewSet
from reviews.models import Category, Genre, Title, Review, Comment


class CategoryViewSet(ListCreateDelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ListCreateDelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related('category').\
        prefetch_related('genre').annotate(rating=Avg('reviews__score'))
    permission_classes = (AdminAnonPermission, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadTitleSerializer
        return WriteTitleSerializer

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


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
