"""صلاحيتين جداد مابيتدوش لحد أوتوماتيك (مدير النظام بيديهم من صفحة الأدوار):
- عرض التقارير
- متابعة كل بيانات الفرع في لوحة التحكم (للمديرين). من غيرها الموظف بيشوف شغله هو بس."""
from django.db import migrations

PERMS = [
    ('view_reports', 'عرض التقارير', 'reports', 'reports'),
    ('view_branch_dashboard', 'متابعة كل بيانات الفرع (لوحة تحكم المدير)', 'core', 'branch_dashboard'),
]


def forwards(apps, schema_editor):
    Permission = apps.get_model('accounts', 'Permission')
    for codename, name, app_label, model_name in PERMS:
        Permission.objects.get_or_create(codename=codename, defaults={
            'name': name, 'app_label': app_label, 'model_name': model_name, 'action': 'view'})


def backwards(apps, schema_editor):
    apps.get_model('accounts', 'Permission').objects.filter(codename__in=[p[0] for p in PERMS]).delete()


class Migration(migrations.Migration):
    dependencies = [('accounts', '0020_password_reset_code')]
    operations = [migrations.RunPython(forwards, backwards)]
