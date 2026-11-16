from django.db import migrations

PREFIXES = {'دبلوم': 'دبلوم', 'دورة': 'دورة', 'دوره': 'دورة'}


def strip_type_prefix(apps, schema_editor):
    """«دبلوم إدارة الموارد البشرية» تبقى: النوع دبلوم + الاسم «إدارة الموارد البشرية»."""
    Master = apps.get_model('courses', 'Master')
    for master in Master.objects.all():
        name = master.name.strip()
        for prefix, program_type in PREFIXES.items():
            rest = name[len(prefix):].strip()
            if name.startswith(prefix + ' ') and rest:
                master.program_type = program_type
                master.name = rest
                master.save(update_fields=['program_type', 'name'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_remove_master_branch'),
    ]

    operations = [
        migrations.RunPython(strip_type_prefix, migrations.RunPython.noop),
    ]
