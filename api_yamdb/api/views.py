from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


from api.filters import TitleFilter
from api.permission import AdminAnonPermission, IsOwnerOrReadOnly
from api.serializers import (CategorySerializer, CommentSerializers,
                             GenreSerializer, ReadTitleSerializer,
                             ReviewSerializer, WriteTitleSerializer)
from api.viewsets import ListCreateDelViewSet
from reviews.models import Category, Genre, Title, Review


class APISignup(APIView):

    pass


class APIToken(APIView):

    pass


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


class UsersViewSet(viewsets.ModelViewSet):
    pass


class CommentViewSet(viewsets.ModelViewSet):
    model = CommentSerializers
    permission_classes = (IsOwnerOrReadOnly,)

    def get_post(self):
        return get_object_or_404(Review, pk=self.kwargs['review_id'])

    def perform_create(self, serializer):
        post = self.get_post()
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

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

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
