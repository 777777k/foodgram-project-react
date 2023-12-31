# Generated by Django 4.2.6 on 2023-10-22 12:49

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(max_length=150, verbose_name='Единицы измерения')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(1, message='Некорректное значение. Минимум 1')], verbose_name='Число Ингредиентов')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название рецепта')),
                ('image', models.ImageField(upload_to=None, verbose_name='Изображение для рецепта')),
                ('text', models.TextField(verbose_name='Описание рецепта')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Время публикации')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Некорректное время приготовления. Минимум 1 минута')], verbose_name='Время приготовления')),
            ],
            options={
                'ordering': ('pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название тэга')),
                ('slug', models.SlugField(max_length=150, unique=True)),
                ('color', models.CharField(default='#49B64E', max_length=7, unique=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='recipes.recipe', verbose_name='Рецепт')),
            ],
        ),
    ]
