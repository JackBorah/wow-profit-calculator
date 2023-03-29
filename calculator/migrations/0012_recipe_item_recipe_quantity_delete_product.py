# Generated by Django 4.1.4 on 2023-01-19 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "calculator",
            "0011_delete_craftingquality_delete_modifiedcraftingitem_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="item",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.item",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="recipe",
            name="quantity",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="Product",
        ),
    ]