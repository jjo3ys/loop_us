# Generated by Django 3.2.5 on 2022-02-07 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_api', '0009_auto_20220207_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banlist',
            name='banlist',
            field=models.JSONField(default=None, null=True),
        ),
    ]