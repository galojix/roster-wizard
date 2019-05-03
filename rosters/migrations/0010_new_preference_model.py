# Generated by Django 2.2 on 2019-05-03 00:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rosters', '0009_manytomany'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preference',
            name='timeslot',
        ),
        migrations.AddField(
            model_name='preference',
            name='day',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='preference',
            name='shift',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='rosters.Shift'),
            preserve_default=False,
        ),
    ]