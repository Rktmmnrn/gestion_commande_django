from rest_framework import permissions
from django.contrib.auth.hashers import check_password

class IsAdminPasswordVerified(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Pour les opérations d'écriture, vérifier le header
        admin_password = request.headers.get('X-Admin-Password')
        if not admin_password:
            return False

        # Vérifier que l'utilisateur est bien un superuser et que le mot de passe correspond
        user = request.user
        if not user.is_authenticated or not user.is_superuser:
            return False

        return check_password(admin_password, user.password)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return IsAdminPasswordVerified().has_permission(request, view)


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated