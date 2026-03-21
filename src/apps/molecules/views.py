import pandas as pd
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Molecule
from .serializers import MoleculeSerializer, MoleculeAdvancedSerializer
from .services import calculate_molecular_properties, molecule_bulk_create


class MoleculeViewSet(viewsets.ModelViewSet):

    queryset = Molecule.objects.all().order_by('nome_molecula')
    serializer_class = MoleculeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome_molecula', 'smiles', 'nome_planta']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MoleculeAdvancedSerializer
        return MoleculeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        user = self.request.user

        if not user.is_authenticated or not user.is_staff:
            queryset = queryset.filter(status_processamento='ok')

        databases = params.getlist('database')
        referencias = params.get('referencia')
        nome_planta = params.get('nome_planta')

        if databases:
            queryset = queryset.filter(database__in=databases)

        if referencias:
            queryset = queryset.filter(referencia__icontains=referencias)

        if nome_planta:
            queryset = queryset.filter(nome_planta__icontains=nome_planta)

        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'databases', 'referencias']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def _processar_rdkit(self, instance, smiles):
        try:
            extra_data = calculate_molecular_properties(smiles)

            if not extra_data:
                instance.status_processamento = 'erro'
                instance.erro_processamento = 'Falha ao interpretar SMILES'
                instance.save()
                return

            for key, value in extra_data.items():
                setattr(instance, key, value)

            instance.status_processamento = 'ok'
            instance.erro_processamento = None
            instance.save()

        except Exception as e:
            instance.status_processamento = 'erro'
            instance.erro_processamento = str(e)
            instance.save()

    def perform_create(self, serializer):
        instance = serializer.save()
        self._processar_rdkit(instance, instance.smiles)

    def perform_update(self, serializer):
        old_smiles = serializer.instance.smiles
        instance = serializer.save()

        if old_smiles != instance.smiles:
            self._processar_rdkit(instance, instance.smiles)

    @action(detail=False, methods=['get'])
    def databases(self, request):
        databases = (
            Molecule.objects
            .values_list('database', flat=True)
            .distinct()
            .order_by('database')
        )
        return Response(databases)

    @action(detail=False, methods=['get'])
    def referencias(self, request):
        referencias = (
            Molecule.objects
            .values_list('referencia', flat=True)
            .distinct()
            .order_by('referencia')
        )
        return Response(referencias)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_excel(self, request, *args, **kwargs):

        if 'file' not in request.FILES:
            return Response({'error': 'Nenhum arquivo enviado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']

        try:
            df = pd.read_excel(file_obj).replace({pd.NA: None})
            data_list = df.to_dict(orient='records')
        except Exception as e:
            return Response({'error': f'Erro ao ler o Excel: {e}'},
                            status=status.HTTP_400_BAD_REQUEST)

        valid_data = []
        errors = []

        for index, item in enumerate(data_list):
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                valid_data.append(serializer.validated_data)
            else:
                errors.append({'linha_excel': index + 2,
                               'erros': serializer.errors})

        if errors:
            return Response({'status': 'falha', 'errors': errors},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            created_molecules = molecule_bulk_create(valid_data)
            return Response({
                'status': 'sucesso',
                'message': f'{len(created_molecules)} moléculas cadastradas.'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Erro no processamento químico: {str(e)}'},
                            status=500)