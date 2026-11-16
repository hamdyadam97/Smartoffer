import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """تجهيز جدول التخصصات للدمج (تغيير الشكل بس). نقل البيانات في 0015 لوحده،
    لأن Postgres مش بيقبل تغيير شكل الجدول وتعديل بياناته في نفس الـ migration."""

    dependencies = [
        ('courses', '0013_strip_type_from_master_name'),
        ('offers', '0012_remove_offerrecipient_prospect'),
        ('core', '0015_drop_prospects_foreign_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='program_type',
            field=models.CharField(choices=[('دبلوم', 'دبلوم'), ('دورة', 'دورة')], db_index=True, default='دبلوم', max_length=20, verbose_name='النوع'),
        ),
        migrations.AddField(
            model_name='course',
            name='period',
            field=models.CharField(blank=True, max_length=100, verbose_name='المدة'),
        ),
        migrations.AlterField(
            model_name='course',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='core.branch', verbose_name='الفرع'),
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together=set(),
        ),
    ]
