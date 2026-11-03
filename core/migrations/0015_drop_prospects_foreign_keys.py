from django.db import migrations

# جداول المستفسرين القديمة (prospects_*) لسه موجودة في قاعدة البيانات بعد ما التطبيق اتشال،
# والـ foreign keys بتاعتها بتمنع حذف التخصصات والدورات والطلاب والفروع والموظفين.
# بنشيل الروابط دي بس، وبيانات المستفسرين نفسها بتفضل زي ما هي.


def drop_prospects_foreign_keys(apps, schema_editor):
    connection = schema_editor.connection
    qn = schema_editor.quote_name
    with connection.cursor() as cursor:
        tables = [t for t in connection.introspection.table_names(cursor) if t.startswith('prospects_')]
        for table in tables:
            constraints = connection.introspection.get_constraints(cursor, table)
            for name, info in constraints.items():
                if info['foreign_key']:
                    schema_editor.execute(f'ALTER TABLE {qn(table)} DROP CONSTRAINT {qn(name)}')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_delete_mastercategory'),
    ]

    operations = [
        migrations.RunPython(drop_prospects_foreign_keys, migrations.RunPython.noop),
    ]
