# Generated by Django 4.0.4 on 2022-06-25 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0026_alter_auction_bid_alter_auction_buyout_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
