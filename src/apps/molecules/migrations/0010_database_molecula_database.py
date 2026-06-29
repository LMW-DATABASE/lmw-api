from django.db import migrations, models
import django.db.models.deletion


def migrate_database_to_many_to_many(apps, schema_editor):
    Molecule = apps.get_model('molecules', 'Molecule')
    Database = apps.get_model('molecules', 'Database')
    MoleculaDatabase = apps.get_model('molecules', 'MoleculaDatabase')

    molecules = (
        Molecule.objects
        .exclude(database__isnull=True)
        .exclude(database='')
        .values('id', 'database')
    )

    for molecule in molecules:
        nome_banco = molecule['database'].strip()
        if not nome_banco:
            continue

        database, _ = Database.objects.get_or_create(nome_banco=nome_banco)
        MoleculaDatabase.objects.get_or_create(
            molecula_id=molecule['id'],
            database_id=database.id,
        )


def migrate_many_to_many_to_database(apps, schema_editor):
    Molecule = apps.get_model('molecules', 'Molecule')
    MoleculaDatabase = apps.get_model('molecules', 'MoleculaDatabase')

    for molecule_id in Molecule.objects.values_list('id', flat=True):
        relation = (
            MoleculaDatabase.objects
            .filter(molecula_id=molecule_id)
            .select_related('database')
            .order_by('database__nome_banco')
            .first()
        )
        Molecule.objects.filter(id=molecule_id).update(
            database=relation.database.nome_banco if relation else '',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0009_molecule_created_by_updated_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_banco', models.CharField(max_length=100, unique=True)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'databases',
                'verbose_name': 'Database',
                'verbose_name_plural': 'Databases',
                'ordering': ('nome_banco',),
            },
        ),
        migrations.CreateModel(
            name='MoleculaDatabase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='molecula_databases', to='molecules.database')),
                ('molecula', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='molecula_databases', to='molecules.molecule')),
            ],
            options={
                'db_table': 'molecula_database',
            },
        ),
        migrations.AddField(
            model_name='molecule',
            name='databases',
            field=models.ManyToManyField(blank=True, related_name='molecules', through='molecules.MoleculaDatabase', to='molecules.database'),
        ),
        migrations.AddConstraint(
            model_name='moleculadatabase',
            constraint=models.UniqueConstraint(fields=('molecula', 'database'), name='unique_molecula_database'),
        ),
        migrations.AlterField(
            model_name='molecule',
            name='database',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.RunPython(
            migrate_database_to_many_to_many,
            migrate_many_to_many_to_database,
        ),
        migrations.RemoveField(
            model_name='molecule',
            name='database',
        ),
    ]
