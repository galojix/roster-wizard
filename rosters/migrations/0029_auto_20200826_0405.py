# Generated by Django 3.1 on 2020-08-26 04:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rosters', '0028_auto_20200826_0353'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staffrule',
            old_name='day_group',
            new_name='daygroup',
        ),
    ]