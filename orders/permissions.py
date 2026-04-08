from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsWaiter(permissions.BasePermission):
    """
    Permission pour les serveurs uniquement.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'waiter'
    
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.role == 'waiter'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Les administrateurs peuvent créer/modifier/supprimer.
    Les serveurs peuvent seulement lire.
    """
    def has_permission(self, request, view):
        # Permettre les requêtes SAFE_METHODS (GET, HEAD, OPTIONS) à tous les authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Les opérations d'écriture nécessitent le rôle admin
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        # Permettre la lecture à tous les authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Les opérations d'écriture nécessitent le rôle admin
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission qui permet à un utilisateur de modifier son propre profil,
    ou à un administrateur de tout modifier.
    """
    def has_object_permission(self, request, view, obj):
        # L'administrateur a tous les droits
        if request.user.role == 'admin':
            return True
        
        # L'utilisateur peut modifier son propre profil
        return obj == request.user