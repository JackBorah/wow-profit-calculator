# Generated by Django 4.0.4 on 2022-06-17 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0012_alter_recipe_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='product_quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
