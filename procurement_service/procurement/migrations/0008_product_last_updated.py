# Generated by Django 5.1.6 on 2025-02-24 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement', '0007_remove_price_last_updated_remove_product_best_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
