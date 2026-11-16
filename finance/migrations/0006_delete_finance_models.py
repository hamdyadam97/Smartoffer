from django.db import migrations


class Migration(migrations.Migration):
    """الجزء المالي اتشال من البرنامج: بنمسح كل جداوله."""

    dependencies = [
        ('finance', '0005_offer_branch'),
    ]

    operations = [
        migrations.DeleteModel(name='Call'),
        migrations.DeleteModel(name='Offer'),
        migrations.DeleteModel(name='Payment'),
        migrations.DeleteModel(name='PaymentOut'),
        migrations.DeleteModel(name='Deposit'),
        migrations.DeleteModel(name='Withdraw'),
        migrations.DeleteModel(name='BillBuy'),
        migrations.DeleteModel(name='BillBuyType'),
    ]
