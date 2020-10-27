#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from common.utils import signer
from common.fields.model import JsonListCharField
from .base import BaseUser
from .asset import Asset


__all__ = ['AdminUser', 'SystemUser']
logger = logging.getLogger(__name__)


class AdminUser(BaseUser):
    """
    A privileged user that ansible can use it to push system user and so on
    """
    BECOME_METHOD_CHOICES = (
        ('sudo', 'sudo'),
        ('su', 'su'),
    )
    become = models.BooleanField(default=True)
    become_method = models.CharField(choices=BECOME_METHOD_CHOICES, default='sudo', max_length=4)
    become_user = models.CharField(default='root', max_length=64)
    _become_pass = models.CharField(default='', blank=True, max_length=128)
    CONNECTIVITY_CACHE_KEY = '_ADMIN_USER_CONNECTIVE_{}'
    _prefer = "admin_user"

    def __str__(self):
        return self.name

    @property
    def become_pass(self):
        password = signer.unsign(self._become_pass)
        if password:
            return password
        else:
            return ""

    @become_pass.setter
    def become_pass(self, password):
        self._become_pass = signer.sign(password)

    @property
    def become_info(self):
        if self.become:
            info = {
                "method": self.become_method,
                "user": self.become_user,
                "pass": self.become_pass,
            }
        else:
            info = None
        return info

    class Meta:
        ordering = ['name']
        unique_together = [('name', 'org_id')]
        verbose_name = _("Admin user")


class SystemUser(BaseUser):
    PROTOCOL_SSH = 'ssh'
    PROTOCOL_RDP = 'rdp'
    PROTOCOL_TELNET = 'telnet'
    PROTOCOL_VNC = 'vnc'
    PROTOCOL_MYSQL = 'mysql'
    PROTOCOL_ORACLE = 'oracle'
    PROTOCOL_MARIADB = 'mariadb'
    PROTOCOL_POSTGRESQL = 'postgresql'
    PROTOCOL_K8S = 'k8s'
    PROTOCOL_CHOICES = (
        (PROTOCOL_SSH, 'ssh'),
        (PROTOCOL_RDP, 'rdp'),
        (PROTOCOL_TELNET, 'telnet'),
        (PROTOCOL_VNC, 'vnc'),
        (PROTOCOL_MYSQL, 'mysql'),
        (PROTOCOL_ORACLE, 'oracle'),
        (PROTOCOL_MARIADB, 'mariadb'),
        (PROTOCOL_POSTGRESQL, 'postgresql'),
        (PROTOCOL_K8S, 'k8s'),
    )

    LOGIN_AUTO = 'auto'
    LOGIN_MANUAL = 'manual'
    LOGIN_MODE_CHOICES = (
        (LOGIN_AUTO, _('Automatic login')),
        (LOGIN_MANUAL, _('Manually login'))
    )
    username_same_with_user = models.BooleanField(default=False, verbose_name=_("Username same with user"))
    nodes = models.ManyToManyField('assets.Node', blank=True, verbose_name=_("Nodes"))
    assets = models.ManyToManyField('assets.Asset', blank=True, verbose_name=_("Assets"))
    users = models.ManyToManyField('users.User', blank=True, verbose_name=_("Users"))
    groups = models.ManyToManyField('users.UserGroup', blank=True, verbose_name=_("User groups"))
    priority = models.IntegerField(default=20, verbose_name=_("Priority"), validators=[MinValueValidator(1), MaxValueValidator(100)])
    protocol = models.CharField(max_length=16, choices=PROTOCOL_CHOICES, default='ssh', verbose_name=_('Protocol'))
    auto_push = models.BooleanField(default=True, verbose_name=_('Auto push'))
    sudo = models.TextField(default='/bin/whoami', verbose_name=_('Sudo'))
    shell = models.CharField(max_length=64,  default='/bin/bash', verbose_name=_('Shell'))
    login_mode = models.CharField(choices=LOGIN_MODE_CHOICES, default=LOGIN_AUTO, max_length=10, verbose_name=_('Login mode'))
    cmd_filters = models.ManyToManyField('CommandFilter', related_name='system_users', verbose_name=_("Command filter"), blank=True)
    sftp_root = models.CharField(default='tmp', max_length=128, verbose_name=_("SFTP Root"))
    token = models.TextField(default='', verbose_name=_('Token'))
    home = models.CharField(max_length=4096, default='', verbose_name=_('Home'), blank=True)
    system_groups = models.CharField(default='', max_length=4096, verbose_name=_('System groups'), blank=True)
    _prefer = 'system_user'

    def __str__(self):
        username = self.username
        if self.username_same_with_user:
            username = 'dynamic'
        return '{0.name}({1})'.format(self, username)

    def get_username(self):
        if self.username_same_with_user:
            return list(self.users.values_list('username', flat=True))
        else:
            return self.username

    @property
    def nodes_amount(self):
        return self.nodes.all().count()

    @property
    def login_mode_display(self):
        return self.get_login_mode_display()

    @property
    def db_application_protocols(self):
        return [
            self.PROTOCOL_MYSQL, self.PROTOCOL_ORACLE, self.PROTOCOL_MARIADB,
            self.PROTOCOL_POSTGRESQL
        ]

    @property
    def k8s_application_protocols(self):
        return [self.PROTOCOL_K8S]

    @property
    def application_category_protocols(self):
        protocols = []
        protocols.extend(self.db_application_protocols)
        protocols.extend(self.k8s_application_protocols)
        return protocols

    def is_need_push(self):
        if self.auto_push and self.protocol in [self.PROTOCOL_SSH, self.PROTOCOL_RDP]:
            return True
        else:
            return False

    @property
    def is_need_cmd_filter(self):
        return self.protocol not in [self.PROTOCOL_RDP, self.PROTOCOL_VNC]

    @property
    def is_need_test_asset_connective(self):
        return self.protocol not in self.application_category_protocols

    @property
    def can_perm_to_asset(self):
        return self.protocol not in self.application_category_protocols

    def _merge_auth(self, other):
        super()._merge_auth(other)
        if self.username_same_with_user:
            self.username = other.username

    @property
    def cmd_filter_rules(self):
        from .cmd_filter import CommandFilterRule
        rules = CommandFilterRule.objects.filter(
            filter__in=self.cmd_filters.all()
        ).distinct()
        return rules

    def is_command_can_run(self, command):
        for rule in self.cmd_filter_rules:
            action, matched_cmd = rule.match(command)
            if action == rule.ACTION_ALLOW:
                return True, None
            elif action == rule.ACTION_DENY:
                return False, matched_cmd
        return True, None

    def get_all_assets(self):
        from assets.models import Node
        nodes_keys = self.nodes.all().values_list('key', flat=True)
        assets_ids = set(self.assets.all().values_list('id', flat=True))
        nodes_assets_ids = Node.get_nodes_all_assets_ids(nodes_keys)
        assets_ids.update(nodes_assets_ids)
        assets = Asset.objects.filter(id__in=assets_ids)
        return assets

    class Meta:
        ordering = ['name']
        unique_together = [('name', 'org_id')]
        verbose_name = _("System user")
