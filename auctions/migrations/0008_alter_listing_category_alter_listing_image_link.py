# Generated by Django 5.1 on 2024-09-17 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_categories_listing_current_alter_listing_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='auctions.categories'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='image_link',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
