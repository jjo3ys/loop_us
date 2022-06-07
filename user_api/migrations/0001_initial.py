# Generated by Django 3.2.5 on 2022-04-15 13:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(default=0)),
                ('target_id', models.PositiveBigIntegerField()),
                ('reason', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Report',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_name', models.CharField(max_length=10)),
                ('type', models.SmallIntegerField(default=0)),
                ('profile_image', models.ImageField(null=True, upload_to='profile_image/')),
                ('department', models.PositiveSmallIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Profile',
            },
        ),
        migrations.CreateModel(
            name='Company_Inform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corp_num', models.CharField(max_length=10)),
                ('corp_name', models.TextField()),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_inform', to='user_api.profile')),
            ],
            options={
                'db_table': 'Corp_inform',
            },
        ),
        migrations.CreateModel(
            name='Banlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banlist', models.JSONField(default=None, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Ban_list',
            },
        ),
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField()),
                ('target_id', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('alarm_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alarm_from', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alarm_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Alarm',
            },
        ),
        migrations.CreateModel(
            name='Activation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corp_num', models.CharField(max_length=10)),
                ('corp_name', models.TextField()),
                ('email', models.TextField()),
                ('name', models.CharField(max_length=10)),
                ('tel_num', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Corp_active',
            },
        ),
    ]
