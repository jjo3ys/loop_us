# Generated by Django 3.2.5 on 2022-01-04 12:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_api', '0003_auto_20220104_1144'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='post',
            table='Posting',
        ),
    ]