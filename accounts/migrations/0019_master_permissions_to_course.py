from django.db import migrations

ACTIONS_AR = {'view': 'عرض', 'add': 'إضافة', 'change': 'تعديل', 'delete': 'حذف'}


def master_perms_to_course(apps, schema_editor):
    """التخصص القديم (master) اتدمج في التخصصات (course): الأدوار اللي كان عندها صلاحية عليه
    بتاخد نفس الصلاحية على التخصصات، وبعدين صلاحيات master والبنوك (الصفحة اتشالت) بتتمسح."""
    Permission = apps.get_model('accounts', 'Permission')
    for master_perm in Permission.objects.filter(model_name='master'):
        course_perm, _ = Permission.objects.get_or_create(
            codename=f'{master_perm.action}_course',
            defaults={
                'name': f'{ACTIONS_AR.get(master_perm.action, master_perm.action)} التخصصات',
                'app_label': 'courses', 'model_name': 'course', 'action': master_perm.action,
            },
        )
        for role in master_perm.roles.all():
            role.permissions.add(course_perm)
    Permission.objects.filter(model_name__in=['master', 'bank']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_remove_teams'),
        ('courses', '0015_delete_master'),
    ]

    operations = [
        migrations.RunPython(master_perms_to_course, migrations.RunPython.noop),
    ]
