# Generated by Django 2.2.6 on 2022-04-10 22:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0003_auto_20220407_2252'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderinfo',
            old_name='order_amount',
            new_name='order_mount',
        ),
    ]
