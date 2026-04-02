# Generated manually for referencia max_length 255 -> 2000

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0003_molecule_estrutura_svg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='molecule',
            name='referencia',
            field=models.CharField(max_length=2000),
        ),
    ]
