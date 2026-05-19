from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0007_molecule_localizacao'),
    ]

    operations = [
        migrations.RenameField(
            model_name='molecule',
            old_name='localizacao',
            new_name='geolocalizacao',
        ),
    ]
