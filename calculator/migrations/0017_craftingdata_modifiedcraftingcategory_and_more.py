# Generated by Django 4.1.4 on 2023-03-08 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0016_craftingquality_spell_recipe_crafting_data_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CraftingData",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name="ModifiedCraftingCategory",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "description",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="item",
            name="optional_material_slot",
        ),
        migrations.RemoveField(
            model_name="item",
            name="vendor_buy_price",
        ),
        migrations.RemoveField(
            model_name="item",
            name="vendor_buy_quantity",
        ),
        migrations.RemoveField(
            model_name="item",
            name="vendor_sell_price",
        ),
        migrations.RemoveField(
            model_name="product",
            name="quality",
        ),
        migrations.AlterField(
            model_name="item",
            name="quality",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.craftingquality",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="recipe_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.recipecategory",
            ),
        ),
        migrations.AlterField(
            model_name="spell",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name="ModifiedCraftingReagentSlot",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "modified_crafting_category",
                    models.ManyToManyField(
                        blank=True, null=True, to="calculator.modifiedcraftingcategory"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModifiedCraftingReagentItem",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "description",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "modified_crafting_category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calculator.modifiedcraftingcategory",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="item",
            name="MCR_item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.modifiedcraftingreagentitem",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="crafting_data",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.craftingdata",
            ),
        ),
    ]