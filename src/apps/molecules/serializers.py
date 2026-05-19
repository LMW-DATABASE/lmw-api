from rest_framework import serializers
from .models import Molecule


class MoleculeSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        default=None,
    )
    updated_by_username = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        default=None,
    )

    class Meta:
        model = Molecule
        fields = [
            'id',
            'nome_molecula',
            'smiles',
            'referencia',
            'nome_planta',
            'database',
            'origem',
            'geolocalizacao',
            'activity',
            'estrutura_svg',
            'status_processamento',
            'erro_processamento',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]
        read_only_fields = [
            'status_processamento',
            'erro_processamento',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]


class MoleculeAdvancedSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        default=None,
    )
    updated_by_username = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        default=None,
    )

    class Meta:
        model = Molecule
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]
