# Generated by Django 3.1.13 on 2021-12-01 11:01

from django.db import migrations

from rbac.builtin import BuiltinRole


def create_builtin_roles(apps, schema_editor):
    BuiltinRole.sync_to_db(show_msg=True)


def set_admin_role(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Role = apps.get_model('rbac', 'Role')
    RoleBinding = apps.get_model('rbac', 'RoleBinding')

    admin = User.objects.filter(username='admin').first()
    if not admin:
        return
    admin_role = Role.objects.filter(name='SystemAdmin').first()
    if admin_role:
        RoleBinding.objects.create(user=admin, role=admin_role, scope='system')

    Organization = apps.get_model('orgs', 'Organization')
    default_org = Organization.objects.filter(id='00000000-0000-0000-0000-000000000002').first()
    org_admin_role = Role.objects.filter(name='OrgAdmin').first()
    if default_org and org_admin_role:
        RoleBinding.objects.create(user=admin, role=org_admin_role, scope='org', org_id=default_org.id)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('orgs', '0001_initial'),
        ('rbac', '0002_auto_20210929_1409'),
    ]

    operations = [
        migrations.RunPython(create_builtin_roles),
        migrations.RunPython(set_admin_role),
    ]
