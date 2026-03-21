from rest_framework import serializers
from .models import Molecule

class MoleculeSerializer(serializers.ModelSerializer):
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
            'activity',
            'estrutura_svg',
            'status_processamento',
            'erro_processamento',
        ]
        read_only_fields = [
            'status_processamento',
            'erro_processamento',
        ]


class MoleculeAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = '__all__'