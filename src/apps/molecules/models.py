from django.db import models

class Molecule(models.Model):
    nome_molecula = models.CharField(max_length=255)
    smiles = models.CharField(max_length=255, unique=True) 
    referencia = models.CharField(max_length=255)
    nome_planta = models.CharField(max_length=255)
    database = models.CharField(max_length=100)

    origem = models.CharField(max_length=255, blank=True, null=True)
    activity = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_molecula