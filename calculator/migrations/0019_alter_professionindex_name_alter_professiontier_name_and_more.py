# Generated by Django 4.0.4 on 2022-06-18 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0018_alter_professiontier_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionindex',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='professiontier',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='recipecategory',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
