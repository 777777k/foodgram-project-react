from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента', max_length=150, unique=True
    )
    measurement_unit = models.CharField(
        max_length=150, verbose_name='Единицы измерения'
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
    name = models.CharField(
        max_length=150, verbose_name='Название тэга', unique=True
    )
    slug = models.SlugField(max_length=150, unique=True)
    color = models.CharField(max_length=7, unique=True, default='#49B64E')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=150, verbose_name='Название рецепта', unique=True
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Изображение для рецепта'
    )
    text = models.TextField('Описание рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
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
                1, message='Некорректное время приготовления. Минимум 1 минута'
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
    amount = models.FloatField(
        verbose_name='Число Ингредиентов',
        validators=(
            MinValueValidator(1, message='Некорректное значение. Минимум 1'),
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
