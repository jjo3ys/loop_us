# Generated by Django 3.1.3 on 2022-02-03 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loop', '0002_auto_20220104_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loopship',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='request',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]