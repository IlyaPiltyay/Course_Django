from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Поле для аватара
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Поле для номера телефона
    country = models.CharField(max_length=50, null=True, blank=True)  # Поле для страны

    USERNAME_FIELD = 'email'  # Используем email вместо username
    REQUIRED_FIELDS = []  # Указываем обязательные поля

    objects = CustomUserManager()  # Подключаем кастомный менеджер

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ('block_user', 'Can block users'),  # Разрешение для блокировки пользователей
        ]

    def __str__(self):
        return self.email