from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Email-адрес', unique=True, max_length=150
    )
    username = models.CharField(
        verbose_name='Имя пользователя', unique=True, max_length=150
    )
    first_name = models.CharField(verbose_name='Имя', max_length=150)
    last_name = models.CharField(verbose_name='Фамилия', max_length=150)
    password = models.CharField(verbose_name='Пароль', max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_follow'
            )
        ]
