from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.core.validators import EmailValidator, RegexValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
# from reviews.validators import validate_correct_username, validate_username


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






class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        """Мета класс пользователя."""

        fields = (
            'bio',
            'email',
            'first_name',
            'last_name',
            'role',
            'username'
        )
        model = User
        validators = [
            EmailValidator,
            RegexValidator(
                regex=r'^[\w.@+-]',
                message='Недопустимый никнейм',
            )
        ]

    def validate_username(self, value):
        """Валидация имени пользователя."""

        name = value.lower()
        if name == 'me':
            raise ValidationError('Имя пользователя "me" запрещено.')
        return value

    def validate_email(self, value):

        if len(value) > 254:
            raise ValidationError("Email не должен быть длиннее 254 символов.")
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        """Мета класс токена."""

        fields = '__all__'
        model = User


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    role = serializers.CharField(read_only=True)

    class Meta:
        """Мета класс пользователя."""

        model = User
        fields = (
            'bio',
            'email',
            'first_name',
            'last_name',
            'role',
            'username'
        )
