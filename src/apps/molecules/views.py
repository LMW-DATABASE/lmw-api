import pandas as pd
from django.utils.timezone import now
from rest_framework import viewsets, filters, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Molecule, MoleculeRequest
from .serializers import (
    MoleculeSerializer,
    MoleculeAdvancedSerializer,
    MoleculeRequestSerializer,
)
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
        """
        Aplica filtros
        """
        queryset = super().get_queryset()
        params = self.request.query_params

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
        """
        Define permissões públicas para leitura e privadas para escrita.
        """
        if self.action in ['list', 'retrieve', 'databases', 'referencias']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Calcula propriedades RDKit 
        """
        smiles = serializer.validated_data.get('smiles')
        extra_data = calculate_molecular_properties(smiles)
        if extra_data:
            serializer.save(**extra_data)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def databases(self, request):
        """
        Retorna a lista de databases 
        """
        databases = (
            Molecule.objects.values_list('database', flat=True).distinct().order_by('database')
        )
        return Response(databases)

    @action(detail=False, methods=['get'])
    def referencias(self, request):
        """
        Retorna a lista de referências
        """
        referencias = (
            Molecule.objects.values_list('referencia', flat=True).distinct().order_by('referencia')
        )
        return Response(referencias)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_excel(self, request, *args, **kwargs):
        """
        Processa upload via Excel 
        """
        if 'file' not in request.FILES:
            return Response({'error': 'Nenhum arquivo enviado.'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj = request.FILES['file']

        try:
            df = pd.read_excel(file_obj).replace({pd.NA: None})
            data_list = df.to_dict(orient='records')
        except Exception as e:
            return Response({'error': f'Erro ao ler o arquivo Excel: {e}'}, status=400)

        valid_data = []
        errors = []

        for index, item in enumerate(data_list):
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                valid_data.append(serializer.validated_data)
            else:
                errors.append({'linha_excel': index + 2, 'erros': serializer.errors})

        if errors:
            return Response({'status': 'falha', 'errors': errors}, status=400)

        try:
            created_molecules = molecule_bulk_create(valid_data)
            return Response(
                {'status': 'sucesso', 'message': f'{len(created_molecules)} moléculas cadastradas com sucesso.'},
                status=201
            )
        except Exception as e:
            return Response({'error': f'Erro no processamento químico: {str(e)}'}, status=500)


class PublicCreateMoleculeRequest(generics.CreateAPIView):
    queryset = MoleculeRequest.objects.all()
    serializer_class = MoleculeRequestSerializer
    permission_classes = [AllowAny]


class AdminListRequests(generics.ListAPIView):
    queryset = MoleculeRequest.objects.all().order_by('-data_requisicao')
    serializer_class = MoleculeRequestSerializer
    permission_classes = [IsAdminUser]


class ApproveRequest(generics.UpdateAPIView):
    queryset = MoleculeRequest.objects.all()
    serializer_class = MoleculeRequestSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "aprovado"
        instance.aprovador = request.user
        instance.data_aprovacao = now()
        instance.motivo_rejeicao = None
        instance.save()
        return Response(MoleculeRequestSerializer(instance).data)


class RejectRequest(generics.UpdateAPIView):
    queryset = MoleculeRequest.objects.all()
    serializer_class = MoleculeRequestSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        motivo = request.data.get("motivo_rejeicao")

        if not motivo:
            return Response({"erro": "motivo_rejeicao é obrigatório"}, status=400)

        instance.status = "rejeitado"
        instance.aprovador = request.user
        instance.data_aprovacao = now()
        instance.motivo_rejeicao = motivo
        instance.save()
        return Response(MoleculeRequestSerializer(instance).data)