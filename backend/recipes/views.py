from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .filters import IngredientFilter, RecipeFilter
from .models import (Recipe, Favorite, ShoppingCart,
                     IngredientRecipe, Ingredient, Tag)
from .permissions import IsAuthenticatedOwnerOrReadOnly
from .serializers import (RecipeSerializer, FollowRecipeSerializer,
                          IngredientSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter, IngredientFilter)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def __favorite_shopping(request, pk, model, errors):
        if request.method == 'POST':
            if model.objects.filter(user=request.user, recipe__id=pk).exists():
                return Response(
                    {'errors': errors['recipe_in']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=request.user, recipe=recipe)
            serializer = FollowRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        recipe = model.objects.filter(user=request.user, recipe__id=pk)
        if recipe.exists():
            recipe.delete()
            return Response(
                {'msg': 'Успешно удалено'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'error': errors['recipe_not_in']},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.__favorite_shopping(request, pk, Favorite, {
            'recipe_in': 'Рецепт уже в избранном',
            'recipe_not_in': 'Рецепта нет в избранном'
        })

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.__favorite_shopping(request, pk, ShoppingCart, {
            'recipe_in': 'Рецепт уже в списке покупок',
            'recipe_not_in': 'Рецепта нет в списке покупок'
        })

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients_obj = (
            IngredientRecipe.objects.filter(recipe__cart__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(sum_amount=Sum('amount'))
        )
        data_dict = {}
        ingredients_list = []

        for item in ingredients_obj:
            name = item['ingredient__name'].capitalize()
            unit = item['ingredient__measurement_unit']
            sum_amount = item['sum_amount']
            data_dict[name] = [sum_amount, unit]

        for ind, (key, value) in enumerate(data_dict.items(), 1):
            ind_str = str(ind).zfill(2)
            ingredients_list.append(
                f'{ind_str}. {key} - {value[0]} {value[1]}'
            )

        filename = 'shopping_list.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('\n'.join(ingredients_list))

        with open(filename, 'rb') as file:
            response = HttpResponse(file.read(), content_type='text/plain')
            response[
                'Content-Disposition'
            ] = f'attachment; filename={filename}'

        return response
