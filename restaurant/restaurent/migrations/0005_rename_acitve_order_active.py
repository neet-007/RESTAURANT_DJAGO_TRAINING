# Generated by Django 4.2.9 on 2024-01-22 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurent', '0004_alter_order_delivery_crew'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='acitve',
            new_name='active',
        ),
    ]
