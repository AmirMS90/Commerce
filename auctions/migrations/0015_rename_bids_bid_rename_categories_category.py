# Generated by Django 5.1 on 2024-09-20 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_bids'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Bids',
            new_name='Bid',
        ),
        migrations.RenameModel(
            old_name='Categories',
            new_name='Category',
        ),
    ]
