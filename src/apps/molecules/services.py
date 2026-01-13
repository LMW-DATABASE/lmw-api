from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, QED
from rdkit.Chem.Scaffolds import MurckoScaffold
from .models import Molecule

def calculate_molecular_properties(smiles: str) -> dict:
    """Lógica pura RDKit para extrair propriedades."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return {}
    
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
    }

def molecule_bulk_create(data_list):
    """
    Processa a lista de dicionários do Excel e salva no banco.
    É esta função que a sua View está procurando.
    """
    molecules_instances = []
    for item in data_list:
        smiles = item.get('smiles')
        if smiles:
            extra_data = calculate_molecular_properties(smiles)
            if extra_data:
                item.update(extra_data)
        molecules_instances.append(Molecule(**item))
    
    return Molecule.objects.bulk_create(molecules_instances)