# Generated by Django 3.1.12 on 2021-09-06 08:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0041_auto_20210906_1524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionjoinrecord',
            name='terminal',
        ),
        migrations.RemoveField(
            model_name='sessionsharing',
            name='terminal',
        ),
    ]
