# Generated by Django 3.1.2 on 2020-10-18 03:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rosters", "0036_unique_together_daygroupday"),
    ]

    operations = [
        migrations.AlterField(
            model_name="daygroup",
            name="name",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
