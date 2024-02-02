from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from rest_framework import serializers
import re

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для валидации полей username и email."""

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        return value

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

    def validate_first_name(self, value):

        if len(value) > 150:
            raise ValidationError("Email не должен быть длиннее 150 символов.")
        return value

    def validate_last_name(self, value):

        if len(value) > 150:
            raise ValidationError("Email не должен быть длиннее 150 символов.")
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

    def validate_email(self, value):

        if len(value) > 254:
            raise ValidationError("Email не должен быть длиннее 254 символов.")
        return value

    def validate_first_name(self, value):

        if len(value) > 150:
            raise ValidationError("Email не должен быть длиннее 150 символов.")
        return value

    def validate_last_name(self, value):

        if len(value) > 150:
            raise ValidationError("Email не должен быть длиннее 150 символов.")
        return value
