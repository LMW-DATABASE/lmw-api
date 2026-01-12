from rest_framework import serializers
from .models import Molecula

class MoleculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecula
        fields = [
            'id', 
            'nome', 
            'smiles', 
            'referencia', 
            'planta', 
            'database', 
            'origem', 
            'atividade'
        ]
class MoleculaAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecula
        fields = '__all__' 