# Generated by Django 3.1.12 on 2021-09-06 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0042_auto_20210906_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionsharing',
            name='link',
        ),
    ]
