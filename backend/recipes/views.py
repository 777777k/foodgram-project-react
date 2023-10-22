from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from .filters import IngredientFilter, RecipeFilter
from .models import (Recipe, Favorite, ShoppingCart,
                     IngredientRecipe, Ingredient, Tag)
from .permissions import IsAuthenticatedOwnerOrReadOnly
from .serializers import (RecipeSerializer, FollowRecipeSerializer,
                          IngredientSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (SearchFilter, IngredientFilter)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def __favorite_shopping(request, pk, model, errors):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if model.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {
                        'errors': errors['recipe_in']
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = FollowRecipeSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if model.objects.filter(user=request.user, recipe=recipe).exists():
            model.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(
                {'msg': 'Успешно удалено'}, status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {
                'error': errors['recipe_not_in']
            }, status=status.HTTP_400_BAD_REQUEST
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
            IngredientRecipe.objects.filter(recipe__carts__user=request.user)
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

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        for line in ingredients_list:
            style = ParagraphStyle(name='Normal', fontSize=12)
            p = Paragraph(line, style)
            story.append(p)
            story.append(Spacer(1, 12))

        pdf.build(story)

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping_list.pdf'

        return response
