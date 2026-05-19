from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Molecule


def _valid_molecule_payload(**overrides):
    data = {
        'nome_molecula': 'Etanol',
        'smiles': 'CCO',
        'referencia': 'ref-test',
        'nome_planta': 'Planta teste',
        'database': 'RAG',
        'origem': '',
        'geolocalizacao': '',
        'activity': '',
    }
    data.update(overrides)
    return data


class MoleculeImportTests(APITestCase):

    def setUp(self):
        self.user_a = User.objects.create_user(
            username='user_a',
            email='user_a@test.com',
            password='pass',
        )
        self.user_b = User.objects.create_user(
            username='user_b',
            email='user_b@test.com',
            password='pass',
        )
        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)
        self.import_url = '/api/molecules/import/'

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_import_without_token_returns_401(self):
        response = self.client.post(
            self.import_url,
            {'molecules': [_valid_molecule_payload()]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_import_missing_molecules_key_returns_400(self):
        self._auth(self.token_a)
        response = self.client.post(self.import_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_empty_molecules_list_returns_400(self):
        self._auth(self.token_a)
        response = self.client.post(
            self.import_url,
            {'molecules': []},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_empty_smiles_returns_400_with_indice(self):
        self._auth(self.token_a)
        payload = _valid_molecule_payload(smiles='')
        response = self.client.post(
            self.import_url,
            {'molecules': [payload]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'falha')
        self.assertEqual(response.data['errors'][0]['indice'], 0)

    def test_import_valid_molecule_creates_record(self):
        self._auth(self.token_a)
        payload = _valid_molecule_payload(smiles='CCC')
        response = self.client.post(
            self.import_url,
            {'molecules': [payload]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'sucesso')
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(response.data['updated'], 0)

        molecule = Molecule.objects.get(smiles='CCC')
        self.assertEqual(molecule.status_processamento, 'ok')
        self.assertEqual(molecule.created_by, self.user_a)
        self.assertEqual(molecule.updated_by, self.user_a)

    def test_import_same_smiles_updates_and_sets_updated_by(self):
        smiles = 'CCO'
        self._auth(self.token_a)
        self.client.post(
            self.import_url,
            {'molecules': [_valid_molecule_payload(smiles=smiles)]},
            format='json',
        )

        self._auth(self.token_b)
        response = self.client.post(
            self.import_url,
            {
                'molecules': [
                    _valid_molecule_payload(
                        smiles=smiles,
                        nome_molecula='Etanol atualizado',
                    )
                ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['updated'], 1)
        self.assertEqual(response.data['created'], 0)

        molecule = Molecule.objects.get(smiles=smiles)
        self.assertEqual(molecule.created_by, self.user_a)
        self.assertEqual(molecule.updated_by, self.user_b)
        self.assertEqual(molecule.nome_molecula, 'Etanol atualizado')

    def test_import_optional_empty_field_becomes_nao_informado(self):
        self._auth(self.token_a)
        payload = _valid_molecule_payload(
            smiles='CCCC',
            origem='',
        )
        self.client.post(
            self.import_url,
            {'molecules': [payload]},
            format='json',
        )
        molecule = Molecule.objects.get(smiles='CCCC')
        self.assertEqual(molecule.origem, 'Não Informado')

    def test_import_validation_failure_does_not_persist_batch(self):
        self._auth(self.token_a)
        response = self.client.post(
            self.import_url,
            {
                'molecules': [
                    _valid_molecule_payload(smiles='CC(C)C'),
                    _valid_molecule_payload(smiles=''),
                ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Molecule.objects.filter(smiles='CC(C)C').exists())


class MoleculeCreateAuditTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='pass',
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_unit_create_sets_created_by_and_updated_by(self):
        response = self.client.post(
            '/api/molecules/',
            _valid_molecule_payload(smiles='c1ccccc1'),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        molecule = Molecule.objects.get(smiles='c1ccccc1')
        self.assertEqual(molecule.created_by, self.user)
        self.assertEqual(molecule.updated_by, self.user)
