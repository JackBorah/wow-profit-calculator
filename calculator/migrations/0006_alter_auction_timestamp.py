# Generated by Django 4.0.4 on 2022-06-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0005_rename_item_modifier_list_itemmodifier_auctions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]