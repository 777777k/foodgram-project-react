from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.core.exceptions import ValidationError

MAX_FIELD_LENGTH = 150


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле "Email" должно быть заполнено')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True.'
            )

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    def set_password(self, raw_password):
        if len(raw_password) > MAX_FIELD_LENGTH:
            raise ValidationError(
                f"Длина пароля не может превышать {MAX_FIELD_LENGTH} символов."
            )
        super().set_password(raw_password)

    email = models.EmailField(
        verbose_name='Email-адрес', unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=MAX_FIELD_LENGTH,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=MAX_FIELD_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=MAX_FIELD_LENGTH
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_FIELD_LENGTH,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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
