# Generated by Django 4.1.4 on 2023-03-08 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calculator", "0017_craftingdata_modifiedcraftingcategory_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="modifiedcraftingreagentslot",
            name="modified_crafting_category",
            field=models.ManyToManyField(to="calculator.modifiedcraftingcategory"),
        ),
    ]