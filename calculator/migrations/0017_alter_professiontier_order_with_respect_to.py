# Generated by Django 4.0.4 on 2022-06-18 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0016_alter_professionindex_options'),
    ]

    operations = [
        migrations.AlterOrderWithRespectTo(
            name='professiontier',
            order_with_respect_to='profession',
        ),
    ]
