# src/apps/molecules/views.py

import pandas as pd
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action # <-- 1. IMPORTE O 'action'
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Molecule
from .serializers import MoleculeSerializer

class MoleculeViewSet(viewsets.ModelViewSet):
    queryset = Molecule.objects.all().order_by('nome_molecula')
    serializer_class = MoleculeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome_molecula']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_excel(self, request, *args, **kwargs):
        """
        Action para fazer o upload em massa de moléculas a partir de um arquivo Excel.
        """
        if 'file' not in request.FILES:
            return Response({'error': 'Nenhum arquivo enviado.'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']

        try:
            df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({'error': f'Erro ao ler o arquivo Excel: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        molecules_to_create = []
        errors = []

        for index, row in df.iterrows():
            data = row.to_dict()
            clean_data = {k: v for k, v in data.items() if pd.notna(v)}
            
            serializer = self.get_serializer(data=clean_data)
            if serializer.is_valid():
                molecules_to_create.append(Molecule(**serializer.validated_data))
            else:
                errors.append({'row': index + 2, 'errors': serializer.errors})

        if errors:
            return Response({'status': 'falha', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        Molecule.objects.bulk_create(molecules_to_create)

        return Response(
            {'status': 'sucesso', 'message': f'{len(molecules_to_create)} moléculas cadastradas com sucesso.'},
            status=status.HTTP_201_CREATED
        )