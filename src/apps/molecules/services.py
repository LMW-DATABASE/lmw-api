from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, QED, Draw
from rdkit.Chem.Scaffolds import MurckoScaffold
from .models import Database, Molecule

WRITABLE_BASE_FIELDS = (
    'nome_molecula',
    'smiles',
    'referencia',
    'nome_planta',
    'origem',
    'geolocalizacao',
    'activity',
)


def normalize_database_names(value):
    if value in (None, ''):
        return []

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        return [str(value).strip()] if str(value).strip() else []

    names = []
    seen = set()
    for raw_name in values:
        if raw_name in (None, ''):
            continue
        name = str(raw_name).strip()
        if not name:
            continue
        key = name.casefold()
        if key not in seen:
            seen.add(key)
            names.append(name)
    return names


def set_molecule_databases(instance, database_names):
    databases = []
    for name in normalize_database_names(database_names):
        database, _ = Database.objects.get_or_create(nome_banco=name)
        databases.append(database)
    instance.databases.set(databases)


def add_molecule_databases(instance, database_names):
    databases = []
    for name in normalize_database_names(database_names):
        database, _ = Database.objects.get_or_create(nome_banco=name)
        databases.append(database)
    instance.databases.add(*databases)


def calculate_molecular_properties(smiles: str) -> dict:
    """Lógica RDKit para extrair propriedades e gerar o desenho 2D em SVG."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {}

    # Gera coordenadas 2D para melhor renderização
    Chem.rdDepictor.Compute2DCoords(mol)

    # Área um pouco maior para moléculas extensas
    drawer = Draw.MolDraw2DSVG(400, 300)

    # Adiciona margem interna para evitar cortes nas bordas
    opts = drawer.drawOptions()
    opts.padding = 0.15

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
        'murcko_scaffold': Chem.MolToSmiles(
            MurckoScaffold.GetScaffoldForMol(mol)
        ),
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


def molecule_bulk_upsert(data_list, user=None):
    """
    Upsert por string SMILES exata (strip). Duplicatas no mesmo lote: última linha prevalece.
    Retorna (created_count, updated_count).
    user: preenche created_by/updated_by quando fornecido.
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
            database_names = item.get('databases', item.get('database'))
            if user is not None:
                instance.updated_by = user
            apply_molecular_properties_to_instance(instance, smiles)
            instance.save()
            if database_names is not None:
                add_molecule_databases(instance, database_names)
            updated_count += 1
        else:
            instance = Molecule()
            for key in WRITABLE_BASE_FIELDS:
                if key in item:
                    setattr(instance, key, item[key])
            database_names = item.get('databases', item.get('database'))
            if user is not None:
                instance.created_by = user
                instance.updated_by = user
            apply_molecular_properties_to_instance(instance, smiles)
            instance.save()
            set_molecule_databases(instance, database_names)
            created_count += 1

    return created_count, updated_count


def molecule_bulk_create(data_list):
    """Legado: cria em lote sem upsert. Preferir molecule_bulk_upsert para import Excel."""
    molecules_instances = []
    for item in data_list:
        item = dict(item)
        smiles = item.get('smiles')
        database_names = item.pop('databases', item.pop('database', []))
        if smiles:
            extra_data = calculate_molecular_properties(smiles)
            if extra_data:
                item.update(extra_data)

        molecule = Molecule.objects.create(**item)
        set_molecule_databases(molecule, database_names)
        molecules_instances.append(molecule)

    return molecules_instances
