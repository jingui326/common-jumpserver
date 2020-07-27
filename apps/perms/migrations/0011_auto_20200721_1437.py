# Generated by Django 2.2.10 on 2020-07-21 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perms', '0010_auto_20191218_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetpermission',
            name='actions',
            field=models.IntegerField(choices=[(255, 'All'), (1, 'Connect'), (2, 'Upload file'), (4, 'Download file'), (6, 'Upload download'), (8, 'GUI copy'), (16, 'GUI paste')], default=255, verbose_name='Actions'),
        ),
    ]
