import django.db.models.deletion
from django.db import migrations, models


def copy_branch_from_master(apps, schema_editor):
    """كل دورة بتاخد فرع التخصص بتاعها (قبل ما التخصص يبقى مشترك بين الفروع)."""
    Course = apps.get_model('courses', 'Course')
    for course in Course.objects.select_related('master'):
        course.branch_id = course.master.branch_id
        course.save(update_fields=['branch'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_drop_prospects_foreign_keys'),
        ('courses', '0010_master_program_type_remove_master_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='core.branch', verbose_name='الفرع'),
        ),
        migrations.RunPython(copy_branch_from_master, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='course',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='core.branch', verbose_name='الفرع'),
        ),
    ]
