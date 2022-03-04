# Generated by Django 3.2.5 on 2022-03-04 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.JSONField(default={})),
            ],
            options={
                'db_table': 'Msg_room',
            },
        ),
        migrations.CreateModel(
            name='Msg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver_id', models.IntegerField()),
                ('message', models.CharField(max_length=1200)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.room')),
            ],
            options={
                'db_table': 'Msg',
            },
        ),
    ]
