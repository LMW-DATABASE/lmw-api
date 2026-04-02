# Remove unique constraint from inchikey (allow same structure, different SMILES strings)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0005_molecule_status_processamento_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='molecule',
            name='inchikey',
            field=models.CharField(blank=True, db_index=True, max_length=27, null=True),
        ),
    ]
