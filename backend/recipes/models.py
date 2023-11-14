from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    MaxValueValidator
)
from django.db import models


User = get_user_model()

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 1440
MAX_FIELD_LENGTH = 150
MIN_INGREDIENT_AMOUNT = 1
MAX_HEX_FIELD_LENGTH = 7


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_FIELD_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_FIELD_LENGTH, verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    color_validator = RegexValidator(
        regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message='Цвет должен быть в формате hex-кода, например, "#RRGGBB"',
    )
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH, verbose_name='Название тэга', unique=True
    )
    slug = models.SlugField(max_length=MAX_FIELD_LENGTH, unique=True)
    color = models.CharField(
        max_length=MAX_HEX_FIELD_LENGTH,
        unique=True,
        default='#49B64E',
        validators=[color_validator],
    )

    class Meta:
        ordering = ['id']
        unique_together = [('color',)]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_FIELD_LENGTH,
        verbose_name='Название рецепта',
        unique=True
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Изображение для рецепта'
    )
    text = models.TextField('Описание рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги', related_name='recipes'
    )
    pub_date = models.DateTimeField(
        verbose_name='Время публикации', auto_now_add=True
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                message='Некорректное время приготовления. Минимум 1 минута'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message='Некорректное время приготовления. Максимум 1440 минут'
            ),
        ),
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Число Ингредиентов',
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message='Некорректное значение. Минимум 1'
            ),
        ),
    )

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            ),
        )
