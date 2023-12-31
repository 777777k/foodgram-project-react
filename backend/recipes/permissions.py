from rest_framework import permissions


class IsAuthenticatedOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user is not None and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
