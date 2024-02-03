from api.permission import AdminOrReadOnly
from rest_framework import filters, mixins, viewsets


class CategoryGenreViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
