# Generated by Django 4.1.4 on 2023-01-15 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0008_delete_craftingstats"),
    ]

    operations = [
        migrations.CreateModel(
            name="CraftingStats",
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
                ("quality", models.IntegerField(blank=True, null=True)),
                ("resourcefulness", models.IntegerField(blank=True, null=True)),
                (
                    "increase_material_from_resourcefulness",
                    models.IntegerField(blank=True, null=True),
                ),
                ("inspiration", models.IntegerField(blank=True, null=True)),
                ("skill_from_inspiration", models.IntegerField(blank=True, null=True)),
                ("multicraft", models.IntegerField(blank=True, null=True)),
                ("skill", models.IntegerField(blank=True, null=True)),
                ("crafting_speed", models.IntegerField(blank=True, null=True)),
                (
                    "item",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calculator.item",
                    ),
                ),
            ],
        ),
    ]
