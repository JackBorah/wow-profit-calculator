# Generated by Django 4.1.4 on 2023-04-24 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0027_alter_modifiedcraftingcategory_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="optionalmaterial",
            name="is_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="region",
            name="region",
            field=models.CharField(
                help_text="us, eu, kr", max_length=30, primary_key=True, serialize=False
            ),
        ),
    ]