
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .base import BaseACL, BaseACLQuerySet


class ACLManager(models.Manager):

    def valid(self):
        return self.get_queryset().valid()


class LoginACL(BaseACL):
    class ActionChoices(models.TextChoices):
        reject = 'reject', _('Reject')
        allow = 'allow', _('Allow')

    name = models.CharField(max_length=128, unique=True, verbose_name=_('Name'))
    # 条件
    ip_group = models.JSONField(default=list, verbose_name=_('Login IP'))
    # 动作
    action = models.CharField(
        max_length=64, choices=ActionChoices.choices, default=ActionChoices.reject,
        verbose_name=_('Action')
    )
    # 关联
    users = models.ManyToManyField('users.User', related_name='login_acls', verbose_name=_('User'))

    objects = ACLManager.from_queryset(BaseACLQuerySet)()

    class Meta:
        ordering = ('priority', '-date_updated', 'name')

    @classmethod
    def get_user_acl(cls, user, action):
        return user.login_acls.filter(action=action).valid().first()
