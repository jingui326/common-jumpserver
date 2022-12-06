# Generated by Django 3.1 on 2021-02-19 04:41

from django.db import migrations

default_id = '00000000-0000-0000-0000-000000000002'


def add_default_org(apps, schema_editor):
    org_cls = apps.get_model('orgs', 'Organization')
    defaults = {'name': 'Default', 'id': default_id}
    org_cls.objects.get_or_create(defaults=defaults, id=default_id)


class Migration(migrations.Migration):
    dependencies = [
        ('orgs', '0002_auto_20180903_1132'),
    ]

    operations = [
        migrations.RunPython(add_default_org),
    ]
