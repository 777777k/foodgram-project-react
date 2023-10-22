from django.contrib import admin
from users.models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name', 'is_superuser',
        'is_active', 'date_joined'
    )
    list_filter = ('email', 'username')
    list_display_links = ('username',)
    search_fields = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('user',)
    search_fields = ('user',)
