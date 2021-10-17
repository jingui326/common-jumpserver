from django.utils.translation import ugettext as _
from rest_framework import serializers
from common.drf.serializers import MethodSerializer
from ..models import LoginACL
from .rules import RuleSerializer

__all__ = ['LoginACLSerializer', ]

common_help_text = _('Format for comma-delimited string, with * indicating a match all. ')


class LoginACLUsersSerializer(serializers.Serializer):
    username_group = serializers.ListField(
        default=[], child=serializers.CharField(max_length=128), label=_('Username'),
        help_text=common_help_text
    )


class LoginACLSerializer(serializers.ModelSerializer):
    user_display = serializers.ReadOnlyField(source='user.name', label=_('Username'))
    reviewers_display = serializers.SerializerMethodField(label=_('Reviewers'))
    action_display = serializers.ReadOnlyField(source='get_action_display', label=_('Action'))
    reviewers_amount = serializers.IntegerField(read_only=True, source='reviewers.count')
    users = LoginACLUsersSerializer(required=False)
    rules = MethodSerializer()

    class Meta:
        model = LoginACL
        fields_mini = ['id', 'name']
        fields_small = fields_mini + [
            'priority', 'rules', 'action', 'action_display',
            'is_active', 'user', 'user_display', 'users',
            'date_created', 'date_updated', 'reviewers_amount',
            'comment', 'created_by'
        ]
        fields_fk = ['user', 'user_display', ]
        fields_m2m = ['reviewers', 'reviewers_display']
        fields = fields_small + fields_fk + fields_m2m
        extra_kwargs = {
            'priority': {'default': 50},
            'is_active': {'default': True},
            "reviewers": {'allow_null': False, 'required': True},
        }

    def get_rules_serializer(self):
        return RuleSerializer()

    def get_reviewers_display(self, obj):
        return ','.join([str(user) for user in obj.reviewers.all()])
