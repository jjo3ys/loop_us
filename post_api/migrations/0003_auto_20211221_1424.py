# Generated by Django 3.2.5 on 2021-12-21 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_api', '0002_auto_20211221_1423'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='contentsimage',
            table='post_image',
        ),
        migrations.AlterModelTable(
            name='like',
            table='post_like',
        ),
    ]
