from django.db import migrations


class Migration(migrations.Migration):
    """التخصصات بقت مشتركة بين كل الفروع، فالفرع اتشال منها."""

    dependencies = [
        ('courses', '0011_course_branch'),
        ('finance', '0005_offer_branch'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='master',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='master',
            name='branch',
        ),
    ]
