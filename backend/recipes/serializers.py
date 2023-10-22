from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow
from .models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Tag, IngredientRecipe
)
from .models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient
        read_only_fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag
        read_only_fields = ('id', 'name', 'color', 'slug')


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.pk).exists()

    class Meta:
        model = User
        fields = '__all__'


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
        fields = '__all__'
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
        fields = '__all__'


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = serializers.ListField(child=serializers.DictField())
    image = serializers.ImageField()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if not ingredients_data:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент')
        elif not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        ingredients_list = []

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')

            ingredient = Ingredient.objects.get(id=ingredient_id)

            if ingredient in ingredients_list:
                raise serializers.ValidationError('Повторяющийся ингредиент')

            ingredients_list.append(
                IngredientRecipe(
                    recipe=recipe, ingredient=ingredient, amount=amount
                )
            )

        IngredientRecipe.objects.bulk_create(ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance = super().update(instance, validated_data)

        if tags:
            instance.tags.set(tags)

        if ingredients_data:
            IngredientRecipe.objects.filter(recipe=instance).delete()

            ingredients_list = []

            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')

                ingredient = Ingredient.objects.get(id=ingredient_id)

                if ingredient in ingredients_list:
                    raise serializers.ValidationError(
                        'Повторяющийся ингредиент'
                    )

                ingredients_list.append(
                    IngredientRecipe(
                        recipe=instance, ingredient=ingredient, amount=amount
                    )
                )

            IngredientRecipe.objects.bulk_create(ingredients_list)

        return instance

    class Meta:
        model = Recipe
        fields = '__all__'


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
