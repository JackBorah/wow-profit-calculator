# Generated by Django 4.0.4 on 2022-06-15 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0007_rename_connected_realm_id_auction_connected_realm'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProfessionTeir',
            new_name='ProfessionTier',
        ),
        migrations.RenameField(
            model_name='recipecatagory',
            old_name='profession_teir',
            new_name='profession_tier',
        ),
    ]
