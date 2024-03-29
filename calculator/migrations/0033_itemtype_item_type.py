# Generated by Django 4.1.4 on 2023-05-26 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0032_alter_professioneffect_amount_craftingreagentquality"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItemType",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        db_index=True, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name="item",
            name="type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.itemtype",
            ),
        ),
    ]
