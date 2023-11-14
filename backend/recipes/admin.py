from django import forms
from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        ingredients = cleaned_data.get('ingredients')

        if not ingredients or len(ingredients) == 0:
            raise forms.ValidationError(
                'Добавьте хотя бы один ингредиент к рецепту.'
            )


class TagAdminForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean_color(self):
        color = self.cleaned_data.get('color')
        color_lower = color.lower()

        existing_tag = Tag.objects.filter(
            color__iexact=color_lower
        ).exclude(id=self.instance.id).first()

        if existing_tag:
            raise forms.ValidationError('Тег с таким цветом уже существует.')

        return color


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_editable = ('color',)
    list_display_links = ('name',)
    search_fields = ('name',)
    form = TagAdminForm


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
    form = RecipeAdminForm

    @admin.display(description='Добавления в избранное')
    def favorite_count(self, recipe):
        return recipe.favorites_recipe.count()


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
