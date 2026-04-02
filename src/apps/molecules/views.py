import pandas as pd
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Molecule
from .serializers import MoleculeSerializer, MoleculeAdvancedSerializer
from .services import calculate_molecular_properties, molecule_bulk_upsert

UPLOAD_EXCEL_REQUIRED_COLUMNS = (
    'nome_molecula',
    'smiles',
    'referencia',
    'nome_planta',
    'database',
)
UPLOAD_EXCEL_OPTIONAL_COLUMNS = ('origem', 'activity')
UPLOAD_EXCEL_TEXT_PLACEHOLDERS = {
    'referencia',
    'nome_planta',
    'database',
    'origem',
    'activity',
}
UPLOAD_EXCEL_EMPTY_TEXT = 'Não Informado'


def _normalize_excel_cell(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return value


def _normalize_upload_excel_row(item):
    normalized = {}
    for key, value in item.items():
        normalized_value = _normalize_excel_cell(value)
        if key in UPLOAD_EXCEL_TEXT_PLACEHOLDERS and normalized_value is None:
            normalized[key] = UPLOAD_EXCEL_EMPTY_TEXT
        else:
            normalized[key] = normalized_value
    return normalized


def _normalize_upload_excel_dataframe(df):
    """
    Mapeia cabeçalhos (case-insensitive, strip) para os nomes esperados pelo serializer.
    Remove colunas que não pertencem ao upload em massa.
    """
    lower_to_actual = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if key not in lower_to_actual:
            lower_to_actual[key] = col

    missing = []
    rename = {}
    for req in UPLOAD_EXCEL_REQUIRED_COLUMNS:
        if req not in lower_to_actual:
            missing.append(req)
        else:
            rename[lower_to_actual[req]] = req

    if missing:
        return None, missing

    for opt in UPLOAD_EXCEL_OPTIONAL_COLUMNS:
        if opt in lower_to_actual:
            rename[lower_to_actual[opt]] = opt

    df = df.rename(columns=rename)
    allowed = set(UPLOAD_EXCEL_REQUIRED_COLUMNS + UPLOAD_EXCEL_OPTIONAL_COLUMNS)
    extra = [c for c in df.columns if c not in allowed]
    if extra:
        df = df.drop(columns=extra, errors='ignore')
    return df, []


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
        except Exception as e:
            return Response({'error': f'Erro ao ler o Excel: {e}'},
                            status=status.HTTP_400_BAD_REQUEST)

        df, missing_cols = _normalize_upload_excel_dataframe(df)
        if missing_cols:
            return Response(
                {
                    'error': 'O ficheiro Excel não contém todas as colunas obrigatórias.',
                    'missing_columns': missing_cols,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data_list = df.to_dict(orient='records')

        valid_data = []
        errors = []

        for index, raw_item in enumerate(data_list):
            item = _normalize_upload_excel_row(raw_item)

            raw_smiles = item.get('smiles')
            smiles_key = (str(raw_smiles).strip() if raw_smiles is not None else '')
            if not smiles_key:
                errors.append({
                    'linha_excel': index + 2,
                    'erros': {'smiles': ['Este campo não pode ser vazio.']},
                })
                continue

            existing = Molecule.objects.filter(smiles=smiles_key).first()
            serializer = self.get_serializer(
                instance=existing,
                data=item,
                partial=(existing is not None),
            )
            if serializer.is_valid():
                valid_data.append(serializer.validated_data)
            else:
                errors.append({'linha_excel': index + 2,
                               'erros': serializer.errors})

        if errors:
            return Response({'status': 'falha', 'errors': errors},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            created_n, updated_n = molecule_bulk_upsert(valid_data)
            parts = []
            if created_n:
                parts.append(f'{created_n} cadastrada(s)')
            if updated_n:
                parts.append(f'{updated_n} atualizada(s)')
            message = ', '.join(parts) if parts else 'Nenhuma alteração.'
            return Response({
                'status': 'sucesso',
                'message': message,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Erro no processamento químico: {str(e)}'},
                            status=500)