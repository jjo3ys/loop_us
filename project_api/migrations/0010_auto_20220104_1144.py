# Generated by Django 3.2.5 on 2022-01-04 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_api', '0009_alter_project_pj_thumbnail'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='project',
            table='Project',
        ),
        migrations.AlterModelTable(
            name='taglooper',
            table='Proj_LooperTag',
        ),
    ]
