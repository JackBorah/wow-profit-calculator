# Generated by Django 4.0.4 on 2022-06-14 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_realm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemmodifier',
            old_name='item_modifier_list',
            new_name='auctions',
        ),
    ]
