from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from common.drf.fields import ObjectRelatedField
from acls.models import CommandGroup, CommandFilterACL
from assets.models import Asset, Account, Platform
from assets.serializers import PlatformSerializer, AssetProtocolsSerializer
from users.models import User
from perms.serializers.permission import ActionChoicesField
from orgs.mixins.serializers import OrgResourceModelSerializerMixin

from ..models import ConnectionToken


__all__ = [
    'ConnectionTokenSecretSerializer',
]


class _ConnectionTokenUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'email']


class _ConnectionTokenAssetSerializer(serializers.ModelSerializer):
    protocols = AssetProtocolsSerializer(many=True, required=False, label=_('Protocols'))

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'address', 'protocols',
            'category', 'type', 'org_id', 'specific'
        ]


class _SimpleAccountSerializer(serializers.ModelSerializer):
    """ Account """

    class Meta:
        model = Account
        fields = ['name', 'username', 'secret_type', 'secret']


class _ConnectionTokenAccountSerializer(serializers.ModelSerializer):
    """ Account """
    su_from = _SimpleAccountSerializer(required=False, label=_('Su from'))

    class Meta:
        model = Account
        fields = [
            'name', 'username', 'secret_type', 'secret', 'su_from',
        ]


class _ConnectionTokenGatewaySerializer(serializers.ModelSerializer):
    """ Gateway """

    class Meta:
        model = Asset
        fields = [
            'id', 'address', 'port',
            # 'username', 'password', 'private_key'
        ]


class _ConnectionTokenCommandFilterACLSerializer(serializers.ModelSerializer):
    command_groups = ObjectRelatedField(
        many=True, required=False, queryset=CommandGroup.objects,
        attrs=('id', 'name', 'type', 'content', 'ignore_case', 'pattern'),
        label=_('Command group')
    )
    reviewers = ObjectRelatedField(
        many=True, queryset=User.objects, label=_("Reviewers"), required=False
    )

    class Meta:
        model = CommandFilterACL
        fields = [
            'id', 'name', 'command_groups', 'action', 'reviewers', 'priority', 'is_active'
        ]


class _ConnectionTokenPlatformSerializer(PlatformSerializer):
    class Meta(PlatformSerializer.Meta):
        model = Platform

    def get_field_names(self, declared_fields, info):
        names = super().get_field_names(declared_fields, info)
        names = [n for n in names if n not in ['automation']]
        return names


class ConnectionTokenSecretSerializer(OrgResourceModelSerializerMixin):
    user = _ConnectionTokenUserSerializer(read_only=True)
    asset = _ConnectionTokenAssetSerializer(read_only=True)
    account = _ConnectionTokenAccountSerializer(read_only=True, source='account_object')
    gateway = _ConnectionTokenGatewaySerializer(read_only=True)
    platform = _ConnectionTokenPlatformSerializer(read_only=True)
    command_filter_acls = _ConnectionTokenCommandFilterACLSerializer(read_only=True, many=True)
    actions = ActionChoicesField()
    expire_at = serializers.IntegerField()
    expire_now = serializers.BooleanField(label=_('Expired now'), write_only=True, default=True)
    connect_method = serializers.SerializerMethodField(label=_('Connect method'))

    class Meta:
        model = ConnectionToken
        fields = [
            'id', 'value', 'user', 'asset', 'account',
            'platform', 'command_filter_acls', 'protocol',
            'gateway', 'actions', 'expire_at', 'expire_now',
            'connect_method'
        ]
        extra_kwargs = {
            'value': {'read_only': True},
        }

    def get_connect_method(self, obj):
        from terminal.const import TerminalType
        from common.utils import get_request_os
        request = self.context.get('request')
        if request:
            os = get_request_os(request)
        else:
            os = 'windows'
        method = TerminalType.get_connect_method(obj.connect_method, protocol=obj.protocol, os=os)
        return method
