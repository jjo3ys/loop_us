# Generated by Django 3.2.5 on 2022-01-04 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_api', '0005_auto_20220104_1223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='p2panswer',
            name='adopt',
        ),
        migrations.RemoveField(
            model_name='p2pquestion',
            name='adopt',
        ),
    ]