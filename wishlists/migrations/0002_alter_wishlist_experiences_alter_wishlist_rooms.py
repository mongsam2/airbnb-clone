# Generated by Django 5.0.4 on 2024-04-27 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0004_experience_category'),
        ('rooms', '0006_room_category'),
        ('wishlists', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='experiences',
            field=models.ManyToManyField(blank=True, to='experiences.experience'),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='rooms',
            field=models.ManyToManyField(blank=True, to='rooms.room'),
        ),
    ]
