# Generated by Django 4.0.4 on 2022-06-17 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0014_alter_recipe_product_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realm',
            name='region',
            field=models.CharField(help_text='North America, Europe, ...', max_length=30),
        ),
    ]