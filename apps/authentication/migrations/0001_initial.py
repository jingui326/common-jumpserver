# Generated by Django 3.2.14 on 2022-12-06 04:52

import uuid

from django.db import migrations, models

import authentication.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessKey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False,
                                        verbose_name='AccessKeyID')),
                ('secret', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='AccessKeySecret')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Access key',
            },
        ),
        migrations.CreateModel(
            name='ConnectionToken',
            fields=[
                ('org_id',
                 models.CharField(blank=True, db_index=True, default='', max_length=36, verbose_name='Organization')),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('updated_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Updated by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('asset', 'Asset'), ('application', 'Application')], default='asset',
                                          max_length=16, verbose_name='Type')),
                ('secret', models.CharField(default='', max_length=64, verbose_name='Secret')),
                ('date_expired',
                 models.DateTimeField(default=authentication.models.date_expired_default, verbose_name='Date expired')),
                ('user_display', models.CharField(default='', max_length=128, verbose_name='User display')),
                ('system_user_display',
                 models.CharField(default='', max_length=128, verbose_name='System user display')),
                ('asset_display', models.CharField(default='', max_length=128, verbose_name='Asset display')),
                ('application_display',
                 models.CharField(default='', max_length=128, verbose_name='Application display')),
            ],
            options={
                'verbose_name': 'Connection token',
                'ordering': ('-date_expired',),
                'permissions': [('view_connectiontokensecret', 'Can view connection token secret')],
            },
        ),
        migrations.CreateModel(
            name='PrivateToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='Key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
            ],
            options={
                'verbose_name': 'Private Token',
            },
        ),
        migrations.CreateModel(
            name='SSOToken',
            fields=[
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('updated_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Updated by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('authkey',
                 models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='Token')),
                ('expired', models.BooleanField(default=False, verbose_name='Expired')),
            ],
            options={
                'verbose_name': 'SSO token',
            },
        ),
        migrations.CreateModel(
            name='TempToken',
            fields=[
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('updated_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Updated by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=128, verbose_name='Username')),
                ('secret', models.CharField(max_length=64, verbose_name='Secret')),
                ('verified', models.BooleanField(default=False, verbose_name='Verified')),
                ('date_verified', models.DateTimeField(null=True, verbose_name='Date verified')),
                ('date_expired', models.DateTimeField(verbose_name='Date expired')),
            ],
            options={
                'verbose_name': 'Temporary token',
            },
        ),
    ]
