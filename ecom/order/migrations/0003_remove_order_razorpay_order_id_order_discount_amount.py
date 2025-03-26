# Generated by Django 5.1.6 on 2025-03-14 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_order_razorpay_payment_id_order_razorpay_signature_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='razorpay_order_id',
        ),
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
