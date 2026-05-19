from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0006_alter_molecule_inchikey_remove_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='molecule',
            name='localizacao',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
