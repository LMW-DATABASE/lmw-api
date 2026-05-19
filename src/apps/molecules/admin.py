from django.contrib import admin
from .models import Molecule
from .services import calculate_molecular_properties

@admin.register(Molecule)
class MoleculeAdmin(admin.ModelAdmin):
    list_display = (
        'nome_molecula',
        'smiles',
        'mw_average',
        'logp',
        'inchikey',
        'formula_molecular',
        'created_by',
        'updated_by',
    )
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
    
    search_fields = ('nome_molecula', 'smiles', 'inchikey', 'nome_planta')
 
    list_filter = ('database', 'origem', 'geolocalizacao')

    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'nome_molecula', 'smiles', 'referencia', 'nome_planta',
                'database', 'origem', 'geolocalizacao', 'activity',
            )
        }),
        ('Auditoria', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
        }),
        ('Dados Técnicos (RDKit)', {
            'classes': ('collapse',),
            'fields': (
                'smiles_canonical', 'inchi', 'inchikey', 'formula_molecular',
                'mw_exact', 'mw_average', 'logp', 'tpsa', 
                'h_bond_donors', 'h_bond_acceptors', 'heavy_atom_count',
                'rotatable_bonds', 'ring_count', 'aromatic_ring_count', 
                'fraction_csp3', 'qed_score', 'np_likeness_score', 'murcko_scaffold'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Garante que, se cadastrada manualmente no admin,
        a molécula também passe pelo RDKit e registra auditoria.
        """
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        if obj.smiles:
            extra_data = calculate_molecular_properties(obj.smiles)
            if extra_data:
                for key, value in extra_data.items():
                    setattr(obj, key, value)
        super().save_model(request, obj, form, change)