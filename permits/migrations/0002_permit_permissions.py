"""صلاحيات المشاهد. الأدوار اللي عندها صلاحية على عروض الأسعار بتاخد نفس الصلاحية على المشاهد."""
from django.db import migrations

ACTIONS = [('view', 'عرض'), ('add', 'إضافة'), ('change', 'تعديل'), ('delete', 'حذف')]
MODELS = [('permit', 'المشاهد'), ('permittemplate', 'قوالب المشاهد')]


def forwards(apps, schema_editor):
    Permission = apps.get_model('accounts', 'Permission')
    Role = apps.get_model('accounts', 'Role')
    for model_name, model_ar in MODELS:
        for action, action_ar in ACTIONS:
            Permission.objects.get_or_create(
                codename=f'{action}_{model_name}',
                defaults={'name': f'{action_ar} {model_ar}', 'app_label': 'permits',
                          'model_name': model_name, 'action': action},
            )
    for action, _ in ACTIONS:
        permit_perm = Permission.objects.get(codename=f'{action}_permit')
        for role in Role.objects.filter(permissions__codename=f'{action}_studentoffer').distinct():
            role.permissions.add(permit_perm)


def backwards(apps, schema_editor):
    apps.get_model('accounts', 'Permission').objects.filter(app_label='permits').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('permits', '0001_initial'),
        ('accounts', '0019_master_permissions_to_course'),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
