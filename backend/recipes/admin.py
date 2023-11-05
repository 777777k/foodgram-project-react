from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_editable = ('color',)
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )
    list_display_links = ('name',)
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'text', 'cooking_time', 'pub_date', 'image',
    )
    list_filter = ('name', 'author', 'tags')
    ordering = ('-pub_date',)
    list_display_links = ('name',)
    search_fields = ('name',)
    inlines = [IngredientRecipeInline]

    @admin.display(description='Добавления в избранное')
    def favorite_count(self, recipe):
        return recipe.favorites_recipe.count()

    def save_model(self, request, obj, form, change):
        if not obj.ingredientrecipe_set.exists():
            self.message_user(
                request,
                "Невозможно сохранить рецепт без ингредиентов.",
                level="ERROR"
            )
        else:
            obj.save()


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_display_links = ('recipe',)
    search_fields = ('recipe',)


@admin.register(Favorite, ShoppingCart)
class FavoriteShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user',)
    search_fields = ('user',)
