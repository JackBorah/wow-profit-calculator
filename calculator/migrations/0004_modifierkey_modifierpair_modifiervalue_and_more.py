# Generated by Django 4.1.4 on 2023-01-03 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0003_alter_auction_buyout_alter_bonuslist_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModifierKey",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        db_index=True, primary_key=True, serialize=False
                    ),
                ),
                ("effect", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ModifierPair",
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
                (
                    "key",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calculator.modifierkey",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModifierValue",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        db_index=True, primary_key=True, serialize=False
                    ),
                ),
                ("effect", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="itemmodifiervalue",
            name="modifier_key",
        ),
        migrations.RemoveField(
            model_name="materialtier",
            name="modifier_key",
        ),
        migrations.RemoveField(
            model_name="secondarystat",
            name="modifier_key",
        ),
        migrations.RemoveField(
            model_name="itembonus",
            name="bonus_list",
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_1_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_10",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_10_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_2_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_3",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_3_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_4",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_4_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_5",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_5_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_6",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_6_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_7",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_7_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_8",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_8_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AddField(
            model_name="bonuslist",
            name="bonus_9",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bonus_9_set",
                to="calculator.itembonus",
            ),
        ),
        migrations.AlterField(
            model_name="bonuslist",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="itembonus",
            name="effect",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="itembonus",
            name="value_0",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="itembonus",
            name="value_1",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="itembonus",
            name="value_2",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="modifierlist",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.DeleteModel(
            name="ItemModifierKey",
        ),
        migrations.DeleteModel(
            name="ItemModifierValue",
        ),
        migrations.DeleteModel(
            name="MaterialTier",
        ),
        migrations.DeleteModel(
            name="SecondaryStat",
        ),
        migrations.AddField(
            model_name="modifierpair",
            name="value",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calculator.modifiervalue",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_1_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_10",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_10_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_2_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_3",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_3_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_4",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_4_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_5",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_5_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_6",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_6_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_7",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_7_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_8",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_8_set",
                to="calculator.modifierpair",
            ),
        ),
        migrations.AddField(
            model_name="modifierlist",
            name="modifier_9",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modifier_9_set",
                to="calculator.modifierpair",
            ),
        ),
    ]