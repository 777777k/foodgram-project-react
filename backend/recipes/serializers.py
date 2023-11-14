from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from drf_base64.fields import Base64ImageField
from django.db import transaction

from users.models import Follow
from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
)
from .models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.pk).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=('ingredient', 'recipe')
            )
        ]


class RecipeListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        queryset = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user.id, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user.id, recipe=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        try:
            return super().to_representation(instance)
        except serializers.ValidationError as exc:
            if 'author' in exc.detail or 'tags' in exc.detail:
                return super().to_representation(instance)
            raise


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeListSerializer(
            instance, context={'request': request}
        )
        return serializer.data

    def validate_ingredients(self, value):
        unique_ingredients = set()

        for ingredient_data in value:
            ingredient_id = ingredient_data.get('id').id

            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными'
                )
            else:
                unique_ingredients.add(ingredient_id)

        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        if not ingredients_data:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент')
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег')

        with transaction.atomic():
            self.validate_ingredients(ingredients_data)

            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)

            ingredients_list = []

            for ingredient_data in ingredients_data:
                amount = ingredient_data.get('amount')
                ingredient_id = ingredient_data.get('id').id
                ingredient = Ingredient.objects.get(id=ingredient_id)

                ingredients_list.append(
                    IngredientRecipe(
                        recipe=recipe, ingredient=ingredient, amount=amount
                    )
                )

            IngredientRecipe.objects.bulk_create(ingredients_list)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if not ingredients_data:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент')
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег')

        self.validate_ingredients(ingredients_data)

        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()

        ingredients_list = []

        for ingredient_data in ingredients_data:
            amount = ingredient_data.get('amount')
            ingredient_id = ingredient_data.get('id').id
            ingredient = Ingredient.objects.get(id=ingredient_id)
            ingredients_list.append(
                IngredientRecipe(
                    recipe=instance, ingredient=ingredient, amount=amount
                )
            )

        IngredientRecipe.objects.bulk_create(ingredients_list)

        return instance

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
