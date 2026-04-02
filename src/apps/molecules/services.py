from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, QED, Draw
from rdkit.Chem.Scaffolds import MurckoScaffold
from .models import Molecule

WRITABLE_BASE_FIELDS = (
    'nome_molecula',
    'smiles',
    'referencia',
    'nome_planta',
    'database',
    'origem',
    'activity',
)


def calculate_molecular_properties(smiles: str) -> dict:
    """Lógica RDKit para extrair propriedades e gerar o desenho 2D em SVG."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {}

    drawer = Draw.MolDraw2DSVG(300, 300)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg_code = drawer.GetDrawingText()

    return {
        'smiles_canonical': Chem.MolToSmiles(mol, isomericSmiles=False),
        'inchi': Chem.MolToInchi(mol),
        'inchikey': Chem.MolToInchiKey(mol),
        'formula_molecular': rdMolDescriptors.CalcMolFormula(mol),
        'mw_exact': Descriptors.ExactMolWt(mol),
        'mw_average': Descriptors.MolWt(mol),
        'logp': Descriptors.MolLogP(mol),
        'tpsa': Descriptors.TPSA(mol),
        'h_bond_donors': Descriptors.NumHDonors(mol),
        'h_bond_acceptors': Descriptors.NumHAcceptors(mol),
        'heavy_atom_count': mol.GetNumHeavyAtoms(),
        'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
        'ring_count': Descriptors.RingCount(mol),
        'aromatic_ring_count': Descriptors.NumAromaticRings(mol),
        'fraction_csp3': Descriptors.FractionCSP3(mol),
        'qed_score': QED.qed(mol),
        'murcko_scaffold': Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(mol)),
        'estrutura_svg': svg_code,
    }


def apply_molecular_properties_to_instance(instance, smiles: str):
    """Atualiza propriedades RDKit e estado de processamento (igual fluxo perform_create/update)."""
    try:
        extra_data = calculate_molecular_properties(smiles)
        if not extra_data:
            instance.status_processamento = 'erro'
            instance.erro_processamento = 'Falha ao interpretar SMILES'
            return

        for key, value in extra_data.items():
            setattr(instance, key, value)

        instance.status_processamento = 'ok'
        instance.erro_processamento = None
    except Exception as e:
        instance.status_processamento = 'erro'
        instance.erro_processamento = str(e)


def molecule_bulk_upsert(data_list):
    """
    Upsert por string SMILES exata (strip). Duplicatas no mesmo lote: última linha prevalece.
    Retorna (created_count, updated_count).
    """
    by_smiles = {}
    for raw in data_list:
        item = dict(raw)
        smiles = (item.get('smiles') or '').strip()
        if not smiles:
            continue
        item['smiles'] = smiles
        by_smiles[smiles] = item

    created_count = 0
    updated_count = 0

    for smiles, item in by_smiles.items():
        instance = Molecule.objects.filter(smiles=smiles).first()

        if instance:
            for key in WRITABLE_BASE_FIELDS:
                if key in item:
                    setattr(instance, key, item[key])
            apply_molecular_properties_to_instance(instance, smiles)
            instance.save()
            updated_count += 1
        else:
            instance = Molecule()
            for key in WRITABLE_BASE_FIELDS:
                if key in item:
                    setattr(instance, key, item[key])
            apply_molecular_properties_to_instance(instance, smiles)
            instance.save()
            created_count += 1

    return created_count, updated_count


def molecule_bulk_create(data_list):
    """Legado: cria em lote sem upsert. Preferir molecule_bulk_upsert para import Excel."""
    molecules_instances = []
    for item in data_list:
        item = dict(item)
        smiles = item.get('smiles')
        if smiles:
            extra_data = calculate_molecular_properties(smiles)
            if extra_data:
                item.update(extra_data)

        molecules_instances.append(Molecule(**item))

    return Molecule.objects.bulk_create(molecules_instances)
