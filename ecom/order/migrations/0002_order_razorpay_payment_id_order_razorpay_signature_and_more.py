# Generated by Django 5.1.6 on 2025-03-11 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='razorpay_signature',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('canceled', 'canceled'), ('delivered', 'delivered'), ('paid', 'paid'), ('failed', 'failed')], default='pending', max_length=10),
        ),
    ]
