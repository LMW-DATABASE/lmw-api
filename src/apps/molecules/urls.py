# src/apps/molecules/urls.py

from django.urls import path
from .views import MoleculeViewSet

urlpatterns = [
    path('molecules/', MoleculeViewSet.as_view({'get': 'list', 'post': 'create'}), name='molecule-list'),
    path('molecules/<int:pk>/', MoleculeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='molecule-detail'),
    path('molecules/upload_excel/', MoleculeViewSet.as_view({'post': 'upload_excel'}), name='molecule-upload-excel'),
]