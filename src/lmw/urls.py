# src/lmw/urls.py

from django.contrib import admin
from django.urls import path, include
from apps.users import views as user_views # Renomeamos para evitar conflito
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/list', user_views.list_users, name='list_users'),
    path('users/register', user_views.create_user, name='create_user'),
    path('users/login', user_views.login_user, name='login_user'),
    path('users/<int:user_id>/set-admin/', user_views.set_admin_role, name='set-admin-role'),


    path('api/', include('apps.molecules.urls')),

    # --- DOCUMENTAÇÃO ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]