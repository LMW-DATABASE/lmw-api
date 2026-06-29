from django.db import migrations


def column_exists(schema_editor, table_name, column_name):
    with schema_editor.connection.cursor() as cursor:
        columns = schema_editor.connection.introspection.get_table_description(
            cursor,
            table_name,
        )
    return column_name in {column.name for column in columns}


class RenameLocalizacaoIfNeeded(migrations.RenameField):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table

        if column_exists(schema_editor, table_name, self.new_name):
            return

        if column_exists(schema_editor, table_name, self.old_name):
            super().database_forwards(app_label, schema_editor, from_state, to_state)
            return

        field = model._meta.get_field(self.new_name)
        schema_editor.add_field(model, field)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        table_name = model._meta.db_table

        if column_exists(schema_editor, table_name, self.old_name):
            return

        if column_exists(schema_editor, table_name, self.new_name):
            super().database_backwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ('molecules', '0007_molecule_localizacao'),
    ]

    operations = [
        RenameLocalizacaoIfNeeded(
            model_name='molecule',
            old_name='localizacao',
            new_name='geolocalizacao',
        ),
    ]
