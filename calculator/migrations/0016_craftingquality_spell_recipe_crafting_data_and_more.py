# Generated by Django 4.1.4 on 2023-02-24 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0015_remove_recipe_item_remove_recipe_quantity_product"),
    ]

    operations = [
        migrations.CreateModel(
            name="CraftingQuality",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("quality_tier", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Spell",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="recipe",
            name="crafting_data",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="quality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.craftingquality",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="spell",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.spell",
            ),
            preserve_default=False,
        ),
    ]