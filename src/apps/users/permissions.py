from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Permite acesso apenas a usuários administradores (is_staff=True).
    """
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado e se é staff
        return request.user and request.user.is_authenticated and request.user.is_staff
