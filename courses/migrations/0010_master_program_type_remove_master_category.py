from django.db import migrations, models


def category_to_program_type(apps, schema_editor):
    """التصنيف القديم بيتحول لنوع: لو اسمه فيه «دور» يبقى دورة، غير كده دبلوم."""
    Master = apps.get_model('courses', 'Master')
    for master in Master.objects.select_related('master_category').exclude(master_category__isnull=True):
        if 'دور' in master.master_category.name:
            master.program_type = 'دورة'
            master.save(update_fields=['program_type'])


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_remove_master_offer_type'),
        ('core', '0013_branch_offer_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='program_type',
            field=models.CharField(choices=[('دبلوم', 'دبلوم'), ('دورة', 'دورة')], db_index=True, default='دبلوم', max_length=20, verbose_name='النوع'),
        ),
        migrations.RunPython(category_to_program_type, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='master',
            name='master_category',
        ),
        migrations.AlterField(
            model_name='master',
            name='name',
            field=models.CharField(db_index=True, max_length=255, verbose_name='اسم الدبلوم / الدورة'),
        ),
    ]
