# Generated by Django 4.1.4 on 2023-01-14 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "calculator",
            "0005_rename_profession_tier_recipecategory_profession_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ModifiedCraftingItem",
            fields=[
                ("item", models.IntegerField(primary_key=True, serialize=False)),
                ("quality", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="ModifiedCraftingSpellSlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("spell", models.IntegerField()),
                ("display_order", models.IntegerField()),
                ("slot", models.IntegerField()),
                ("quantity", models.IntegerField()),
                ("recraft_quantity", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Spell",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name="optionalmaterial",
            name="item_tier",
        ),
        migrations.RemoveField(
            model_name="optionalmaterial",
            name="slot",
        ),
        migrations.RenameField(
            model_name="material",
            old_name="item_name",
            new_name="name",
        ),
        migrations.RenameField(
            model_name="optionalmaterialslot",
            old_name="slot_name",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="craftingstats",
            name="id",
        ),
        migrations.RemoveField(
            model_name="item",
            name="item_tier",
        ),
        migrations.RemoveField(
            model_name="material",
            name="item_tier",
        ),
        migrations.RemoveField(
            model_name="product",
            name="item_tier",
        ),
        migrations.AddField(
            model_name="craftingstats",
            name="crafting_speed",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="craftingstats",
            name="increase_material_from_resourcefulness",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="craftingstats",
            name="quality",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="craftingstats",
            name="skill",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="craftingstats",
            name="skill_from_inspiration",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="item",
            name="optional_material_slot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.optionalmaterialslot",
            ),
        ),
        migrations.AddField(
            model_name="material",
            name="display_order",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="material",
            name="optional_material_slot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.optionalmaterialslot",
            ),
        ),
        migrations.AddField(
            model_name="material",
            name="recraft_quantity",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="item",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.item",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="craftingstats",
            name="item",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to="calculator.item",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="quality",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="material",
            name="quantity",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name="ItemTier",
        ),
        migrations.DeleteModel(
            name="OptionalMaterial",
        ),
        migrations.AddField(
            model_name="recipe",
            name="spell",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.spell",
            ),
            preserve_default=False,
        ),
    ]