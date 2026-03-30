from rest_framework import serializers
from .models import Molecule, MoleculeRequest

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
            'estrutura_svg'
        ]


class MoleculeAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = '__all__'


class MoleculeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoleculeRequest
        fields = '__all__'
        read_only_fields = [
            'status',
            'aprovador',
            'data_requisicao',
            'data_aprovacao',
            'motivo_rejeicao'
        ]