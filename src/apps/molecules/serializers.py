# src/apps/molecules/serializers.py

from rest_framework import serializers
from .models import Molecule

class MoleculeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Molecule
        fields = '__all__' 