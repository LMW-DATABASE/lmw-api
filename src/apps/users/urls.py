# src/apps/users/urls.py

from django.urls import path
# Importamos todas as views que você criou
from .views import create_user, login_user, set_admin_role, list_users

urlpatterns = [
    # URL para cadastro -> aciona a função create_user
    path('register', create_user, name='register'),

    # URL para login -> aciona a função login_user
    path('login', login_user, name='login'),

    # URLs para as outras funções que você já tinha
    path('users-list', list_users, name='users-list'),
    path('set-admin/<int:user_id>', set_admin_role, name='set-admin'),
]