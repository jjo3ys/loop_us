# Generated by Django 3.2.5 on 2022-03-04 12:17

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
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=50)),
                ('introduction', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('pj_thumbnail', models.ImageField(default=None, null=True, upload_to='project/%Y%m%d/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Project',
            },
        ),
        migrations.CreateModel(
            name='TagLooper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('looper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='looper', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='looper', to='project_api.project')),
            ],
            options={
                'db_table': 'Proj_LooperTag',
            },
        ),
    ]
