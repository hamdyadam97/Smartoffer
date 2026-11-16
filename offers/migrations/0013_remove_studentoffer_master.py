import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """العرض بقى مربوط بالتخصص (courses.Course) بس، بعد ما بياناته اتنقلت في courses 0014."""

    dependencies = [
        ('offers', '0012_remove_offerrecipient_prospect'),
        ('courses', '0015_merge_master_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentoffer',
            name='master',
        ),
        migrations.AlterField(
            model_name='studentoffer',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='offers', to='courses.course', verbose_name='التخصص'),
        ),
    ]
