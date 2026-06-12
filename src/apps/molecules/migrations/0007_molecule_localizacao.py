from django.db import migrations, models


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(
            cursor,
            table_name,
        )
    return column_name in {column.name for column in columns}


class AddLocalizacaoIfNeeded(migrations.AddField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table
        if (
            column_exists(schema_editor, table_name, 'localizacao')
            or column_exists(schema_editor, table_name, 'geolocalizacao')
        ):
            return
        super().database_forwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0006_alter_molecule_inchikey_remove_unique'),
    ]

    operations = [
        AddLocalizacaoIfNeeded(
            model_name='molecule',
            name='localizacao',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
