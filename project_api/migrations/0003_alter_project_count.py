# Generated by Django 3.2.6 on 2021-11-08 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_api', '0002_auto_20211108_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='count',
            field=models.IntegerField(default=1),
        ),
    ]