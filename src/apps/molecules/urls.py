# src/apps/molecules/urls.py

from django.urls import path
from .views import MoleculeViewSet

urlpatterns = [
    path('', MoleculeViewSet.as_view({'get': 'list', 'post': 'create'}), name='molecule-list'),
    path('upload_excel/', MoleculeViewSet.as_view({'post': 'upload_excel'}), name='molecule-upload-excel'), 
    path('<int:pk>/', MoleculeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='molecule-detail'),
]