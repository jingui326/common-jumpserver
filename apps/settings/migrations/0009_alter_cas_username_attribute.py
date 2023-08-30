# Generated by Django 3.2.19 on 2023-06-30 10:37
import json

from django.db import migrations


def migrate_cas_setting(apps, schema_editor):
    setting_model = apps.get_model('settings', 'Setting')
    obj = setting_model.objects.filter(name='CAS_RENAME_ATTRIBUTES').first()
    if obj:
        try:
            value = json.loads(obj.value)
        except Exception:
            print("Invalid telnet regex setting, skip")
            return

        if value.pop('uid', None):
            setting_model.objects.filter(name='CAS_USERNAME_ATTRIBUTE').update(value='"cas:user"')
            value['cas:user'] = 'username'
            obj.value = json.dumps(value)
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0008_alter_setting_options'),
    ]

    operations = [
        migrations.RunPython(migrate_cas_setting),
    ]
