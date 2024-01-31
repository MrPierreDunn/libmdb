from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import (validate_year)
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание', blank=True, null=True
    )
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'
        ordering = ('category',)

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(verbose_name='Текст')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, 'Значение рейтинга не может быть ниже 1.'),
            MaxValueValidator(10, 'Значение рейтинга не может быть выше 10.')
        ],
        verbose_name='Рейтинг'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации отзыва'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Отзыв {self.author.username} на {self.title.name}'


class Comment(models.Model):
    text = models.TextField(verbose_name='text')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарии',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
        null=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
