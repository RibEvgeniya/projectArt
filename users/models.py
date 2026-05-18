from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Расширенная модель пользователя"""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, null=True, blank=True, verbose_name='О себе')
    is_creator = models.BooleanField(default=False, verbose_name='Творец')
    is_moderator = models.BooleanField(default=False, verbose_name='Модератор')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='Город')
    website = models.URLField(null=True, blank=True, verbose_name='Сайт')

    following = models.ManyToManyField(
        'self', symmetrical=False, related_name='followers',
        blank=True, verbose_name='Подписки'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


from django.db import models

# Create your models here.
