# Generated by Django 4.0.4 on 2022-06-15 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0008_rename_professionteir_professiontier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipecatagory',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
