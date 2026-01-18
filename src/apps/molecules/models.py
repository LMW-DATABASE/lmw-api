from django.db import models

class Molecule(models.Model):
    nome_molecula = models.CharField(max_length=255)
    smiles = models.CharField(max_length=500, unique=True) 
    referencia = models.CharField(max_length=255)
    nome_planta = models.CharField(max_length=255)
    database = models.CharField(max_length=100)
    origem = models.CharField(max_length=255, blank=True, null=True)
    activity = models.TextField(blank=True, null=True)

    # ---  Identificadores Estruturais ---
    smiles_canonical = models.CharField(max_length=500, blank=True, null=True)
    inchi = models.TextField(blank=True, null=True)
    inchikey = models.CharField(max_length=27, unique=True, db_index=True, blank=True, null=True)
    formula_molecular = models.CharField(max_length=100, blank=True, null=True)

    # ---  Dados de Massa ---
    mw_exact = models.FloatField(blank=True, null=True)
    mw_average = models.FloatField(blank=True, null=True)

    # ---  Propriedades Físico-Químicas ---
    logp = models.FloatField(blank=True, null=True)
    tpsa = models.FloatField(blank=True, null=True)
    h_bond_donors = models.IntegerField(blank=True, null=True)
    h_bond_acceptors = models.IntegerField(blank=True, null=True)

    # ---Características de Estrutura (Topologia) ---
    heavy_atom_count = models.IntegerField(blank=True, null=True)
    rotatable_bonds = models.IntegerField(blank=True, null=True)
    ring_count = models.IntegerField(blank=True, null=True)
    aromatic_ring_count = models.IntegerField(blank=True, null=True)
    fraction_csp3 = models.FloatField(blank=True, null=True)

    # --- Scores e Diferenciais ---
    qed_score = models.FloatField(blank=True, null=True)
    np_likeness_score = models.FloatField(blank=True, null=True)
    murcko_scaffold = models.CharField(max_length=500, blank=True, null=True)

    # --- Representação Visual ---
    estrutura_svg = models.TextField(blank=True, null=True)

    # --- Metadados ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_molecula