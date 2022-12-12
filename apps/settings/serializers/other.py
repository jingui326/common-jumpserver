from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class OtherSettingSerializer(serializers.Serializer):
    PREFIX_TITLE = _('More...')

    EMAIL_SUFFIX = serializers.CharField(
        required=False, max_length=1024, label=_("Email suffix"),
        help_text=_('This is used by default if no email is returned during SSO authentication')
    )

    OTP_ISSUER_NAME = serializers.CharField(
        required=False, max_length=16, label=_('OTP issuer name'),
    )
    OTP_VALID_WINDOW = serializers.IntegerField(
        min_value=1, max_value=10,
        label=_("OTP valid window")
    )

    WINDOWS_SSH_DEFAULT_SHELL = serializers.ChoiceField(
        choices=[
            ('cmd', _("CMD")),
            ('powershell', _("PowerShell"))
        ],
        label=_('Shell (Windows)'),
        help_text=_('The shell type used when Windows assets perform ansible tasks')
    )

    PERM_SINGLE_ASSET_TO_UNGROUP_NODE = serializers.BooleanField(
        required=False, label=_("Perm ungroup node"),
        help_text=_("Perm single to ungroup node")
    )

    TICKET_AUTHORIZE_DEFAULT_TIME = serializers.IntegerField(
        min_value=1, max_value=999999, required=False,
        label=_("Ticket authorize default time")
    )
    TICKET_AUTHORIZE_DEFAULT_TIME_UNIT = serializers.ChoiceField(
        choices=[('day', _("day")), ('hour', _("hour"))],
        label=_("Ticket authorize default time unit"), required=False,
    )
    HELP_DOCUMENT_URL = serializers.URLField(
        required=False, allow_blank=True, allow_null=True, label=_("Help Docs URL"),
        help_text=_('default: http://docs.jumpserver.org')
    )

    HELP_SUPPORT_URL = serializers.URLField(
        required=False, allow_blank=True, allow_null=True, label=_("Help Support URL"),
        help_text=_('default: http://www.jumpserver.org/support/')
    )
    DOWNLOAD_MEMORY_LIMIT = serializers.IntegerField(
        min_value=1, max_value=99999, required=False, default=1024,
        label=_('Download Memory limit'),
        help_text=_("Maximum memory usage of download resources (Unit MB).")
    )

    # 准备废弃
    # PERIOD_TASK_ENABLED = serializers.BooleanField(
    #     required=False, label=_("Enable period task")
    # )
