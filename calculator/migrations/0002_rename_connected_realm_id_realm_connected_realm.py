# Generated by Django 4.0.4 on 2022-06-08 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='realm',
            old_name='connected_realm_id',
            new_name='connected_realm',
        ),
    ]
