from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from .models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
            'tags': ['exact'],
        }

    def custom_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            if name == 'is_favorited':
                return queryset.filter(
                    favorites_recipe__user=self.request.user
                )
            elif name == 'is_in_shopping_cart':
                return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = []
