# Adds status_processamento and erro_processamento — present in model but missing from earlier migrations

from django.db import migrations, models


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(
            cursor,
            table_name,
        )
    return column_name in {column.name for column in columns}


class AddFieldIfNotExists(migrations.AddField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        field = model._meta.get_field(self.name)
        if column_exists(schema_editor, model._meta.db_table, field.column):
            return
        super().database_forwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0004_alter_molecule_referencia_max_length'),
    ]

    operations = [
        AddFieldIfNotExists(
            model_name='molecule',
            name='status_processamento',
            field=models.CharField(
                choices=[('ok', 'Processada'), ('erro', 'Erro RDKit')],
                default='ok',
                max_length=10,
            ),
        ),
        AddFieldIfNotExists(
            model_name='molecule',
            name='erro_processamento',
            field=models.TextField(blank=True, null=True),
        ),
    ]
