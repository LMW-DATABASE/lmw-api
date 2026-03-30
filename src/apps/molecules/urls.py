# src/apps/molecules/urls.py

from django.urls import path
from .views import (
    MoleculeViewSet,
    PublicCreateMoleculeRequest,
    AdminListRequests,
    ApproveRequest,
    RejectRequest,
)

urlpatterns = [
    path('', MoleculeViewSet.as_view({'get': 'list', 'post': 'create'}), name='molecule-list'),
    path('upload_excel/', MoleculeViewSet.as_view({'post': 'upload_excel'}), name='molecule-upload-excel'),
    path('<int:pk>/', MoleculeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='molecule-detail'),

    # Requests públicas
    path('requests/public/create/', PublicCreateMoleculeRequest.as_view(), name='request-create'),

    # Admin
    path('requests/admin/list/', AdminListRequests.as_view(), name='request-list'),
    path('requests/admin/<int:pk>/approve/', ApproveRequest.as_view(), name='request-approve'),
    path('requests/admin/<int:pk>/reject/', RejectRequest.as_view(), name='request-reject'),
]