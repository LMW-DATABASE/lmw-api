from rest_framework import serializers
from .models import Database, Molecule


def normalize_database_names(value):
    if value in (None, ''):
        return []

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        raise serializers.ValidationError('Informe um nome ou uma lista de databases.')

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
    for name in database_names:
        database, _ = Database.objects.get_or_create(nome_banco=name)
        databases.append(database)

    instance.databases.set(databases)


def add_molecule_databases(instance, database_names):
    databases = []
    for name in database_names:
        database, _ = Database.objects.get_or_create(nome_banco=name)
        databases.append(database)

    instance.databases.add(*databases)


class DatabaseNamesField(serializers.Field):
    def to_internal_value(self, data):
        names = normalize_database_names(data)
        if not names:
            raise serializers.ValidationError('Informe ao menos um database.')
        return names

    def to_representation(self, value):
        return [database.nome_banco for database in value.all()]


class MoleculeSerializer(serializers.ModelSerializer):
    database = DatabaseNamesField(source='databases', required=True)
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        default=None,
    )
    updated_by_username = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        default=None,
    )

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
            'geolocalizacao',
            'activity',
            'estrutura_svg',
            'status_processamento',
            'erro_processamento',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]
        read_only_fields = [
            'status_processamento',
            'erro_processamento',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]
        extra_kwargs = {
            'smiles': {'validators': []},
        }

    def validate_smiles(self, value):
        smiles = value.strip()
        if self.instance is not None:
            exists = (
                Molecule.objects
                .filter(smiles=smiles)
                .exclude(pk=self.instance.pk)
                .exists()
            )
            if exists:
                raise serializers.ValidationError(
                    'Outra molécula com este smiles já existe.'
                )
        return smiles

    def create(self, validated_data):
        database_names = validated_data.pop('databases', [])
        smiles = validated_data.get('smiles')
        instance = Molecule.objects.filter(smiles=smiles).first()

        if instance is not None:
            created_by = validated_data.pop('created_by', None)
            updated_by = validated_data.pop('updated_by', None)

            for key, value in validated_data.items():
                setattr(instance, key, value)

            if instance.created_by_id is None and created_by is not None:
                instance.created_by = created_by
            if updated_by is not None:
                instance.updated_by = updated_by

            instance.save()
            add_molecule_databases(instance, database_names)
            return instance

        instance = super().create(validated_data)
        set_molecule_databases(instance, database_names)
        return instance

    def update(self, instance, validated_data):
        database_names = validated_data.pop('databases', None)
        instance = super().update(instance, validated_data)
        if database_names is not None:
            set_molecule_databases(instance, database_names)
        return instance


class MoleculeAdvancedSerializer(serializers.ModelSerializer):
    database = DatabaseNamesField(source='databases', required=True)
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        default=None,
    )
    updated_by_username = serializers.CharField(
        source='updated_by.username',
        read_only=True,
        default=None,
    )

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
            'geolocalizacao',
            'activity',
            'smiles_canonical',
            'inchi',
            'inchikey',
            'formula_molecular',
            'mw_exact',
            'mw_average',
            'logp',
            'tpsa',
            'h_bond_donors',
            'h_bond_acceptors',
            'heavy_atom_count',
            'rotatable_bonds',
            'ring_count',
            'aromatic_ring_count',
            'fraction_csp3',
            'qed_score',
            'np_likeness_score',
            'murcko_scaffold',
            'estrutura_svg',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
            'status_processamento',
            'erro_processamento',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_username',
            'updated_by_username',
        ]
        extra_kwargs = {
            'smiles': {'validators': []},
        }

    def validate_smiles(self, value):
        smiles = value.strip()
        if self.instance is not None:
            exists = (
                Molecule.objects
                .filter(smiles=smiles)
                .exclude(pk=self.instance.pk)
                .exists()
            )
            if exists:
                raise serializers.ValidationError(
                    'Outra molécula com este smiles já existe.'
                )
        return smiles

    def create(self, validated_data):
        database_names = validated_data.pop('databases', [])
        smiles = validated_data.get('smiles')
        instance = Molecule.objects.filter(smiles=smiles).first()

        if instance is not None:
            created_by = validated_data.pop('created_by', None)
            updated_by = validated_data.pop('updated_by', None)

            for key, value in validated_data.items():
                setattr(instance, key, value)

            if instance.created_by_id is None and created_by is not None:
                instance.created_by = created_by
            if updated_by is not None:
                instance.updated_by = updated_by

            instance.save()
            add_molecule_databases(instance, database_names)
            return instance

        instance = super().create(validated_data)
        set_molecule_databases(instance, database_names)
        return instance

    def update(self, instance, validated_data):
        database_names = validated_data.pop('databases', None)
        instance = super().update(instance, validated_data)
        if database_names is not None:
            set_molecule_databases(instance, database_names)
        return instance
