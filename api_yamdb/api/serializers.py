from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from reviews.validators import validate_correct_username, validate_username


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объекта класса User."""

    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[validate_correct_username, validate_username]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
    )

    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('email', 'username')


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для объекта класса User при получении токена JWT."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class AbstractTitleSerializer(serializers.ModelSerializer):
    """Абстрактная модель сериализатора."""

    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description',
            'genre', 'category'
        )


class ReadTitleSerializer(AbstractTitleSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)


class WriteTitleSerializer(AbstractTitleSerializer):
    """Сериализатор объектов класса Title при небезопасных запросах."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    def to_representation(self, instance):
        return ReadTitleSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (request.method == 'POST' and Review.objects.filter(
                author=request.user, title=title).exists()):
            raise ValidationError(
                'Нельзя сделать 2 отзыва на одно произведение!'
            )
        return data


class CommentSerializers(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', )


class UsersSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        lookup_field = 'username'


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели профиля."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        lookup_field = 'username'
        read_only_fields = ('role',)
