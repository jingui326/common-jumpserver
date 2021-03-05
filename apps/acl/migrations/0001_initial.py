# Generated by Django 3.1 on 2021-03-05 08:07

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAssetACL',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('priority', models.IntegerField(default=50, help_text='1-100, the higher will be match first', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Priority')),
                ('comment', models.TextField(blank=True, default='', max_length=128, verbose_name='Comment')),
                ('users', models.JSONField(verbose_name='User')),
                ('system_users', models.JSONField(verbose_name='System User')),
                ('assets', models.JSONField(verbose_name='Asset')),
                ('action', models.CharField(choices=[('login_confirm', 'Login confirm')], default='login_confirm', max_length=64, verbose_name='Action')),
                ('reviewers', models.ManyToManyField(blank=True, related_name='review_login_asset_confirm_acl', to=settings.AUTH_USER_MODEL, verbose_name='Reviewers')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LoginACL',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True, verbose_name='Created by')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('priority', models.IntegerField(default=50, help_text='1-100, the higher will be match first', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Priority')),
                ('comment', models.TextField(blank=True, default='', max_length=128, verbose_name='Comment')),
                ('ip_group', models.JSONField(default=list, verbose_name='Login IP')),
                ('action', models.CharField(choices=[('reject', 'Reject')], default='reject', max_length=64, verbose_name='Action')),
                ('users', models.ManyToManyField(related_name='login_acl', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
