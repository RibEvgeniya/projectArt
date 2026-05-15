from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Расширенная модель пользователя
    """
    # Добавляем дополнительные поля
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    cover = models.ImageField(
        upload_to='covers/',
        null=True,
        blank=True,
        verbose_name='Шапка профиля'
    )
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='О себе'
    )
    is_creator = models.BooleanField(
        default=False,
        verbose_name='Творец'
    )
    is_moderator = models.BooleanField(
        default=False,
        verbose_name='Модератор'
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Телефон'
    )
    location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Город'
    )
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name='Сайт'
    )
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        verbose_name='Подписки'
    )
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username