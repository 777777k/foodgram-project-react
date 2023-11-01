from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import User, Follow
from recipes.serializers import FollowRecipeSerializer


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if (
            'request' not in self.context
            or self.context['request'].user.is_anonymous
        ):
            return False
        return Follow.objects.filter(
            author=obj, user=self.context['request'].user
        ).exists()

    def validate(self, data):
        password = data.get('password')
        user = User(**data)
        try:
            validate_password(password=password, user=user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Follow.objects.filter(
            author=obj, user=self.context['request'].user
        ).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        author = User.objects.get(id=obj.pk)
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = FollowRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializer.data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class FollowCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all()
    )

    def validate(self, data):
        user = data['user']
        author = data['author']
        if self.context['request'].method == 'POST' and user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора'
            )
        ]
