# Generated by Django 3.1 on 2020-09-08 23:32

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('rosters', '0035_auto_20200827_0124'),
        ('users', '0009_auto_20200827_0147'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', users.models.CustomUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, null=True, to='rosters.Role'),
        ),
    ]