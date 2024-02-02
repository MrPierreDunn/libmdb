from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from rest_framework import serializers

from users.models import User


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
                regex=r'^[\w.@+-]+',
                message='Недопустимый никнейм',
            )
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save
        return user

    def validate_username(self, value):
        """Валидация имени пользователя."""

        if value == 'me':
            raise ValidationError('Имя пользователя "me" запрещено.')
        return value

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
