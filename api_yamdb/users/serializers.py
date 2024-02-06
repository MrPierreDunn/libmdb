from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import User
from users.validators import validate_username_uniqueness
from users.constsans import (MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH)


class UserCreateSerializer(serializers.Serializer):
    """Базовый сериализатор для валидации полей username и email."""

    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH, required=True)
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        required=True
    )

    def validate_username(self, value):
        validate_username_uniqueness(value)
        return value

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
