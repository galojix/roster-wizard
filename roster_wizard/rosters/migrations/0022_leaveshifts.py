# Generated by Django 2.2.4 on 2019-09-02 23:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rosters", "0021_blankshiftsequence"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="timeslot",
            options={"ordering": ("date", "shift__shift_type")},
        ),
    ]
