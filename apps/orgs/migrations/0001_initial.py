# Generated by Django 4.1.13 on 2024-05-09 03:16

from django.db import migrations, models
import orgs.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('created_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='Created by')),
                ('updated_by', models.CharField(blank=True, max_length=128, null=True, verbose_name='Updated by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('comment', models.TextField(blank=True, default='', verbose_name='Comment')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('builtin', models.BooleanField(default=False, verbose_name='Builtin')),
            ],
            options={
                'verbose_name': 'Organization',
                'permissions': (('view_rootorg', 'Can view root org'), ('view_alljoinedorg', 'Can view all joined org')),
            },
            bases=(orgs.models.OrgRoleMixin, models.Model),
        ),
    ]
