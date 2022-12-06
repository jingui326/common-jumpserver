# Generated by Django 3.1.14 on 2022-04-02 08:27

import django.db
from django.db import migrations, models


def migrate_to_host(apps, schema_editor):
    asset_model = apps.get_model("assets", "Asset")
    host_model = apps.get_model("assets", 'Host')
    db_alias = schema_editor.connection.alias

    count = 0
    batch_size = 1000

    while True:
        assets = asset_model.objects.using(db_alias).all()[count:count + batch_size]
        if not assets:
            break
        count += len(assets)
        hosts = [host_model(asset_ptr=asset) for asset in assets]
        host_model.objects.using(db_alias).bulk_create(hosts, ignore_conflicts=True)


def migrate_hardware_info(apps, *args):
    asset_model = apps.get_model("assets", "Asset")

    count = 0
    batch_size = 1000
    hardware_fields = [
        'vendor', 'model', 'sn', 'cpu_model', 'cpu_count', 'cpu_cores',
        'cpu_vcpus', 'memory', 'disk_total', 'disk_info', 'os', 'os_arch',
        'os_version', 'hostname_raw', 'number'
    ]

    while True:
        assets = asset_model.objects.all()[count:count + batch_size]
        if not assets:
            break
        count += len(assets)

        updated = []
        for asset in assets:
            info = {field: getattr(asset, field) for field in hardware_fields if getattr(asset, field)}
            if not info:
                continue
            asset.info = info
            updated.append(asset)
        asset_model.objects.bulk_update(updated, ['info'])


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0003_auto_20180109_2331'),
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='info',
            field=models.JSONField(blank=True, default=dict, verbose_name='Info'),
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='hostname',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ['name'],
                     'permissions': [('refresh_assethardwareinfo', 'Can refresh asset hardware info'),
                                     ('test_assetconnectivity', 'Can test asset connectivity'),
                                     ('push_assetsystemuser', 'Can push system user to asset'),
                                     ('match_asset', 'Can match asset'), ('add_assettonode', 'Add asset to node'),
                                     ('move_assettonode', 'Move asset to node')], 'verbose_name': 'Asset'},
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='ip',
            new_name='address',
        ),
        migrations.AddField(
            model_name='asset',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Date updated'),
        ),
        migrations.AddField(
            model_name='asset',
            name='updated_by',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Updated by'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='created_by',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by'),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('asset_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='assets.asset')),
            ],
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('asset_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='assets.asset')),
                ('db_name', models.CharField(blank=True, max_length=1024, verbose_name='Database')),
            ],
            options={
                'verbose_name': 'Database',
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('asset_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='assets.asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='Cloud',
            fields=[
                ('asset_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='assets.asset')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='Web',
            fields=[
                ('asset_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='assets.asset')),
                ('autofill', models.CharField(choices=[('no', 'Disabled'), ('basic', 'Basic'), ('script', 'Script')],
                                              default='basic', max_length=16, verbose_name='Autofill')),
                ('password_selector',
                 models.CharField(blank=True, default='', max_length=128, verbose_name='Password selector')),
                ('submit_selector',
                 models.CharField(blank=True, default='', max_length=128, verbose_name='Submit selector')),
                ('username_selector',
                 models.CharField(blank=True, default='', max_length=128, verbose_name='Username selector')),
                ('script', models.JSONField(blank=True, default=list, verbose_name='Script')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.asset',),
        ),
        migrations.RunPython(migrate_hardware_info),
        migrations.RunPython(migrate_to_host),
    ]
