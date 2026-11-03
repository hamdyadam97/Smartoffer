from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_branch_offer_template'),
        ('courses', '0010_master_program_type_remove_master_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MasterCategory',
        ),
    ]
