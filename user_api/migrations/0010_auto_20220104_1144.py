# Generated by Django 3.2.5 on 2022-01-04 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_api', '0009_alter_company_inform_table'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='company_inform',
            table='Prof_company_inform',
        ),
        migrations.AlterModelTable(
            name='profile',
            table='Profile',
        ),
    ]
