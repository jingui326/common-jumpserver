# Generated by Django 3.2.14 on 2022-11-18 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0022_alter_applyassetticket_apply_actions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applyassetticket',
            name='apply_actions',
            field=models.IntegerField(default=31, verbose_name='Actions'),
        ),
    ]
