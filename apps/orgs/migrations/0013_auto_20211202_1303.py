# Generated by Django 3.1.13 on 2021-12-02 05:03

from django.db import migrations

from rbac.const import BuiltinRole


def migrate_to_new_role(apps, schema_editor):
    org_member_model = apps.get_model('orgs', 'OrganizationMember')
    members = org_member_model.objects.all()

    print()
    for role_name in ['Admin', 'Auditor', 'User']:
        role_members = members.filter(_role=role_name)
        print("Migrate org role members: {} {}".format(role_name, role_members.count()))
        role = BuiltinRole.get_org_role_by_old_name(role_name)
        role_members.update(role=role.id)


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0012_auto_20211202_1130'),
        ('rbac', '0004_auto_20211201_1901'),
    ]

    operations = [
        migrations.RunPython(migrate_to_new_role)
    ]
