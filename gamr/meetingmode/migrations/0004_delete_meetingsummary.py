# Generated by Django 3.0.3 on 2020-05-13 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetingmode', '0003_meetingsummary'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MeetingSummary',
        ),
    ]
