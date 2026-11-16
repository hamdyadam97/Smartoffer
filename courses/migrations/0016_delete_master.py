from django.db import migrations, models


class Migration(migrations.Migration):
    """بعد نقل البيانات (0014) التخصص القديم مالوش لازمة."""

    dependencies = [
        ('courses', '0015_merge_master_data'),
        ('offers', '0013_remove_studentoffer_master'),
        ('finance', '0006_delete_finance_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='master',
        ),
        migrations.DeleteModel(
            name='Master',
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-created_at'], 'verbose_name': 'تخصص', 'verbose_name_plural': 'التخصصات'},
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(db_index=True, max_length=255, verbose_name='الاسم'),
        ),
        migrations.AlterField(
            model_name='course',
            name='program_type',
            field=models.CharField(choices=[('دبلوم', 'دبلوم'), ('دورة', 'دورة')], db_index=True, default='دبلوم', max_length=20, verbose_name='النوع'),
        ),
    ]
