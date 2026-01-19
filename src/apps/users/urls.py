from django.urls import path
from .views import create_user, login_user, set_admin_role, list_users

urlpatterns = [
    path('register/', create_user, name='register'),
    path('login/', login_user, name='login'),
    
    path('list/', list_users, name='users-list'),
    
    path('<int:user_id>/set-admin/', set_admin_role, name='set-admin'),
]