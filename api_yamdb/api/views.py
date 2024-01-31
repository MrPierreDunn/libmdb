from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.response import Response


from api.filters import TitleFilter
from api.permission import AdminAnonPermission
from api.serializers import (CategorySerializer, GenreSerializer,
                             ReadTitleSerializer, WriteTitleSerializer)
from api.viewsets import ListCreateDelViewSet
from reviews.models import Category, Genre, Title


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
