# Adds status_processamento and erro_processamento — present in model but missing from earlier migrations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0004_alter_molecule_referencia_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='molecule',
            name='status_processamento',
            field=models.CharField(
                choices=[('ok', 'Processada'), ('erro', 'Erro RDKit')],
                default='ok',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='molecule',
            name='erro_processamento',
            field=models.TextField(blank=True, null=True),
        ),
    ]
