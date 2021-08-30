# coding: utf-8
#

from django_filters import rest_framework as filters
from django.db.models import F, Q

from common.drf.filters import BaseFilterSet
from common.drf.api import JMSModelViewSet
from ..models import Account
from ..hands import IsOrgAdminOrAppUser, IsOrgAdmin, NeedMFAVerify
from .. import serializers


class AccountFilterSet(BaseFilterSet):
    username = filters.CharFilter(field_name='username')
    type = filters.CharFilter(field_name='type', lookup_expr='exact')
    category = filters.CharFilter(field_name='category', lookup_expr='exact')
    app_display = filters.CharFilter(field_name='app_display', lookup_expr='exact')

    class Meta:
        model = Account
        fields = ['app', 'systemuser']

    @property
    def qs(self):
        qs = super().qs
        qs = self.filter_username(qs)
        return qs

    def filter_username(self, qs):
        username = self.get_query_param('username')
        if not username:
            return qs
        qs = qs.filter(Q(username=username) | Q(systemuser__username=username)).distinct()
        return qs


class ApplicationAccountViewSet(JMSModelViewSet):
    model = Account
    search_fields = ['username', 'app_display']
    filterset_class = AccountFilterSet
    filterset_fields = ['', 'username', 'app_display', 'type', 'category', 'app']
    serializer_class = serializers.AppAccountSerializer
    permission_classes = (IsOrgAdmin,)
    http_method_names = ['get', 'put', 'patch', 'options']

    def get_queryset(self):
        queryset = Account.objects.all() \
            .annotate(type=F('app__type')) \
            .annotate(app_display=F('app__name')) \
            .annotate(systemuser_display=F('systemuser__name')) \
            .annotate(category=F('app__category'))
        return queryset


class ApplicationAccountSecretViewSet(ApplicationAccountViewSet):
    serializer_class = serializers.AppAccountSecretSerializer
    permission_classes = [IsOrgAdminOrAppUser, NeedMFAVerify]
    http_method_names = ['get', 'options']
