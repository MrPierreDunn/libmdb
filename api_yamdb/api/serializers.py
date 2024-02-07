from django.forms import ValidationError
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import User
from users.validators import validate_username_uniqueness
from users.constsans import (MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH)

from reviews.models import Category, Comment, Genre, Review, Title


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

    rating = serializers.IntegerField(
        default=None,
        read_only=True,
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description',
            'genre', 'category',
        )


class ReadTitleSerializer(AbstractTitleSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta(AbstractTitleSerializer.Meta):
        pass


class WriteTitleSerializer(AbstractTitleSerializer):
    """Сериализатор объектов класса Title при небезопасных запросах."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta(AbstractTitleSerializer.Meta):
        pass

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
        if request.method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(
            author=request.user,
            title_id=title_id
        ).exists():
            raise ValidationError(
                'Нельзя сделать 2 отзыва на одно произведение!'
            )
        return data


class CommentSerializers(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserCreateSerializer(serializers.Serializer):
    """Базовый сериализатор для валидации полей username и email."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH, required=True)
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[validate_username_uniqueness],
        required=True
    )

    def create(self, validated_data):
        try:
            user, created = User.objects.get_or_create(**validated_data)
            confirmation_code = default_token_generator.make_token(user)
            send_mail(
                'Код подтверждения',
                f'Код подтверждения: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [validated_data['email']],
                fail_silently=False,
            )
            return user
        except IntegrityError as e:
            raise serializers.ValidationError({'detail': str(e)})

    class Meta:
        model = User
        fields = ('username', 'email',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        """Мета класс пользователя."""

        fields = (
            'bio',
            'first_name',
            'last_name',
            'role',
            'email',
            'username'
        )
        model = User


class TokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        """
        Проверка confirmation_code.
        """
        user = get_object_or_404(User, username=data['username'])
        confirmation_code = data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            raise ValidationError('Неверный код подтверждения')
        return data


class MeSerializer(UserSerializer):
    """Сериализатор пользователя."""

    class Meta(UserSerializer.Meta):
        """Мета класс пользователя."""

        read_only_fields = ('role',)