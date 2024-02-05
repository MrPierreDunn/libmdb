from rest_framework import filters, mixins, viewsets

from api.permission import AdminOrReadOnly


class CategoryGenreViewSet(mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = (AdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=name',)
