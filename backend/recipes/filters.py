from django_filters import rest_framework as filters
from .models import Recipe
from rest_framework.filters import SearchFilter


class RecipeFilter(filters.FilterSet):
    tags__slug = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='in'
    )

    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
        }

    def custom_filter(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            if name == 'is_favorited':
                return queryset.filter(
                    favorites__user=self.request.user
                )
            elif name == 'is_in_shopping_cart':
                return queryset.filter(cart__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    search_param = 'name'
