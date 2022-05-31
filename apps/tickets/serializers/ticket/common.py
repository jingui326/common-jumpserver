from django.db.transaction import atomic
from django.utils.translation import ugettext as _
from rest_framework import serializers

from orgs.utils import tmp_to_org
from tickets.models import Ticket

__all__ = ['DefaultPermissionName', 'get_default_permission_name', 'BaseApplyAssetApplicationSerializer']


def get_default_permission_name(ticket):
    name = ''
    if isinstance(ticket, Ticket):
        name = _('Created by ticket ({}-{})').format(ticket.title, str(ticket.id)[:4])
    return name


class DefaultPermissionName(object):
    default = None

    @staticmethod
    def _construct_default_permission_name(serializer_field):
        permission_name = ''
        ticket = serializer_field.root.instance
        if isinstance(ticket, Ticket):
            permission_name = get_default_permission_name(ticket)
        return permission_name

    def set_context(self, serializer_field):
        self.default = self._construct_default_permission_name(serializer_field)

    def __call__(self):
        return self.default


class BaseApplyAssetApplicationSerializer(serializers.Serializer):
    permission_model: None

    def validate(self, attrs):
        attrs = super().validate(attrs)

        apply_date_start = attrs['apply_date_start'].strftime('%Y-%m-%d %H:%M:%S')
        apply_date_expired = attrs['apply_date_expired'].strftime('%Y-%m-%d %H:%M:%S')

        if apply_date_expired <= apply_date_start:
            error = _('The expiration date should be greater than the start date')
            raise serializers.ValidationError({'apply_date_expired': error})

        attrs['apply_date_start'] = apply_date_start
        attrs['apply_date_expired'] = apply_date_expired
        return attrs

    @atomic
    def create(self, validated_data):
        instance = super().create(validated_data)
        name = _('Created by ticket ({}-{})').format(instance.title, str(instance.id)[:4])
        with tmp_to_org(instance.org_id):
            if not self.permission_model.objects.filter(name=name).exists():
                instance.meta.update({'apply_permission_name': name})
                return instance
        raise serializers.ValidationError(_('Permission named `{}` already exists'.format(name)))
