from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_api', '0007_remove_profile_class_num'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='profile',
            table='profile',
        ),
        migrations.CreateModel(
            name='Company_Inform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corp_num', models.CharField(max_length=10)),
                ('corp_name', models.TextField()),
                ('tel_num', models.CharField(max_length=13)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_api.profile')),
            ],
        ),
    ]