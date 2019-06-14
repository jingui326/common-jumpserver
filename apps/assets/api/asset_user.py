# -*- coding: utf-8 -*-
#

import time

from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django.shortcuts import get_object_or_404

from common.permissions import IsOrgAdminOrAppUser
from common.utils import get_object_or_none, get_logger
from common.mixins import IDInCacheFilterMixin
from ..backends import AssetUserManager
from ..models import Asset, Node, SystemUser, AdminUser
from .. import serializers
from ..tasks import test_asset_users_connectivity_manual


__all__ = [
    'AssetUserViewSet', 'AssetUserAuthInfoApi', 'AssetUserTestConnectiveApi',
    'AssetUserExportViewSet',
]


logger = get_logger(__name__)


class AssetUserFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        for field in view.filter_fields:
            value = request.GET.get(field)
            if not value:
                continue
            if field in ("node_id", "system_user_id", "admin_user_id"):
                continue
            kwargs[field] = value
        return queryset.filter(**kwargs)


class AssetUserFilterFromBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        system_user_id = request.GET.get("system_user_id")
        admin_user_id = request.GET.get("admin_user_id")
        if not system_user_id and not admin_user_id:
            return queryset

        if system_user_id:
            system_user = get_object_or_404(SystemUser, id=system_user_id)
            assets = system_user.assets.all()
            queryset = queryset.filter(asset__in=assets, username=system_user.username)

        if admin_user_id:
            admin_user = get_object_or_404(AdminUser, id=admin_user_id)
            assets = admin_user.assets.all()
            queryset = queryset.filter(asset__in=assets, username=admin_user.username)
        return queryset


class AssetUserSearchBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        value = request.GET.get('search')
        if not value:
            return queryset
        _queryset = AssetUserManager.none()
        for field in view.search_fields:
            if field in ("node_id", "system_user_id", "admin_user_id"):
                continue
            _queryset |= queryset.filter(**{field: value})
        return _queryset


class AssetUserViewSet(IDInCacheFilterMixin, viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    serializer_class = serializers.AssetUserSerializer
    permission_classes = (IsOrgAdminOrAppUser, )
    http_method_names = ['get', 'post']
    filter_fields = [
        "id", "ip", "hostname", "username", "asset_id", "node_id",
        "system_user_id", "admin_user_id"
    ]
    search_fields = filter_fields
    filter_backends = (
        filters.OrderingFilter, AssetUserFilterBackend, AssetUserSearchBackend,
        AssetUserFilterFromBackend,
    )

    def get_queryset(self):
        # 尽可能先返回更少的数据
        username = self.request.GET.get('username')
        asset_id = self.request.GET.get('asset_id')
        node_id = self.request.GET.get('node_id')
        kwargs = {}
        assets = []
        if username:
            kwargs['username'] = username

        if asset_id:
            asset = get_object_or_none(Asset, pk=asset_id)
            kwargs['assets'] = [asset]
        elif node_id:
            node = get_object_or_404(Node, id=node_id)
            assets = node.assets.all()

        if assets:
            kwargs['assets'] = assets
        manger = AssetUserManager()
        queryset = manger.filter(**kwargs)
        return queryset


class AssetUserExportViewSet(AssetUserViewSet):
    serializer_class = serializers.AssetUserExportSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        otp_last_verify = request.session.get("OTP_LAST_VERIFY_TIME")
        if not otp_last_verify or time.time() - int(otp_last_verify) > 600:
            return Response({"error": "Need MFA confirm mfa auth"}, status=403)
        return super().list(request, *args, **kwargs)


class AssetUserAuthInfoApi(generics.RetrieveAPIView):
    serializer_class = serializers.AssetUserAuthInfoSerializer
    permission_classes = (IsOrgAdminOrAppUser,)

    def retrieve(self, request, *args, **kwargs):
        otp_last_verify = request.session.get("OTP_LAST_VERIFY_TIME")
        if not otp_last_verify or time.time() - int(otp_last_verify) > 600:
            return Response({"error": "Need MFA confirm mfa auth"}, status=403)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        status_code = status.HTTP_200_OK
        if not instance:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(serializer.data, status=status_code)

    def get_object(self):
        username = self.request.GET.get('username')
        asset_id = self.request.GET.get('asset_id')
        asset = get_object_or_none(Asset, pk=asset_id)
        try:
            manger = AssetUserManager()
            instance = manger.get(username, [asset])
        except Exception as e:
            logger.error(e, exc_info=True)
            return None
        else:
            return instance


class AssetUserTestConnectiveApi(generics.RetrieveAPIView):
    """
    Test asset users connective
    """

    def get_asset_users(self):
        username = self.request.GET.get('username')
        asset_id = self.request.GET.get('asset_id')
        asset = get_object_or_none(Asset, pk=asset_id)
        manager = AssetUserManager()
        asset_users = manager.filter(username=username, assets=[asset])
        return asset_users

    def retrieve(self, request, *args, **kwargs):
        asset_users = self.get_asset_users()
        task = test_asset_users_connectivity_manual.delay(asset_users)
        return Response({"task": task.id})



