from django.db import migrations

# صلاحيات أقسام اتشالت من البرنامج: تصنيفات التخصصات والمستفسرون
REMOVED_MODELS = ['mastercategory', 'prospect', 'prospectoffer']


def delete_permissions(apps, schema_editor):
    Permission = apps.get_model('accounts', 'Permission')
    Permission.objects.filter(model_name__in=REMOVED_MODELS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_remove_team_branch'),
    ]

    operations = [
        migrations.RunPython(delete_permissions, migrations.RunPython.noop),
    ]
