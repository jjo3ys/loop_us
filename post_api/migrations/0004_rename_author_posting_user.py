# Generated by Django 3.2.5 on 2021-12-21 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_api', '0003_alter_posting_project'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posting',
            old_name='author',
            new_name='user',
        ),
    ]
