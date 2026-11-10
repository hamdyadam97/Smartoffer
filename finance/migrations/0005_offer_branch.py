import django.db.models.deletion
from django.db import migrations, models


def copy_branch_from_master(apps, schema_editor):
    """كل عرض سعر بياخد فرع التخصص بتاعه (قبل ما التخصص يبقى مشترك بين الفروع)."""
    Offer = apps.get_model('finance', 'Offer')
    for offer in Offer.objects.select_related('master'):
        offer.branch_id = offer.master.branch_id
        offer.save(update_fields=['branch'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_drop_prospects_foreign_keys'),
        ('courses', '0011_course_branch'),
        ('finance', '0004_call_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='price_offers', to='core.branch', verbose_name='الفرع'),
        ),
        migrations.RunPython(copy_branch_from_master, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='offer',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='price_offers', to='core.branch', verbose_name='الفرع'),
        ),
    ]
