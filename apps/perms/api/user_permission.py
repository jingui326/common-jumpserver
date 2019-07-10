# -*- coding: utf-8 -*-
#
import time
import traceback
import uuid
from hashlib import md5
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView, Response
from rest_framework.generics import (
    ListAPIView, get_object_or_404, RetrieveAPIView
)
from rest_framework.pagination import LimitOffsetPagination

from common.permissions import IsValidUser, IsOrgAdminOrAppUser
from common.tree import TreeNodeSerializer
from common.utils import get_logger, get_object_or_none
from ..utils import (
    AssetPermissionUtil, ParserNode,
)
from .. import const
from ..hands import User, Asset, Node, SystemUser, NodeSerializer
from .. import serializers
from ..models import Action


logger = get_logger(__name__)

__all__ = [
    'UserGrantedAssetsApi', 'UserGrantedNodesApi',
    'UserGrantedNodesWithAssetsApi', 'UserGrantedNodeAssetsApi',
    'ValidateUserAssetPermissionApi', 'UserGrantedNodesAsTreeApi',
    'UserGrantedNodesWithAssetsAsTreeApi', 'GetUserAssetPermissionActionsApi',
]


class UserPermissionCacheMixin:
    cache_policy = '0'
    RESP_CACHE_KEY = '_PERMISSION_RESPONSE_CACHE_V2_{}'
    CACHE_TIME = settings.ASSETS_PERM_CACHE_TIME
    _object = None

    def get_object(self):
        return None

    # 内部使用可控制缓存
    def _get_object(self):
        if not self._object:
            self._object = self.get_object()
        return self._object

    def get_object_id(self):
        obj = self._get_object()
        if obj:
            return str(obj.id)
        return None

    def get_request_md5(self):
        path = self.request.path
        query = {k: v for k, v in self.request.GET.items()}
        query.pop("_", None)
        query = "&".join(["{}={}".format(k, v) for k, v in query.items()])
        full_path = "{}?{}".format(path, query)
        return md5(full_path.encode()).hexdigest()

    def get_meta_cache_id(self):
        obj = self._get_object()
        util = AssetPermissionUtil(obj, cache_policy=self.cache_policy)
        meta_cache_id = util.cache_meta.get('id')
        return meta_cache_id

    def get_response_cache_id(self):
        obj_id = self.get_object_id()
        request_md5 = self.get_request_md5()
        meta_cache_id = self.get_meta_cache_id()
        resp_cache_id = '{}_{}_{}'.format(obj_id, request_md5, meta_cache_id)
        return resp_cache_id

    def get_response_from_cache(self):
        # 没有数据缓冲
        meta_cache_id = self.get_meta_cache_id()
        if not meta_cache_id:
            logger.debug("Not get meta id: {}".format(meta_cache_id))
            return None
        # 从响应缓冲里获取响应
        key = self.get_response_key()
        data = cache.get(key)
        if not data:
            logger.debug("Not get response from cache: {}".format(key))
            return None
        logger.debug("Get user permission from cache: {}".format(self.get_object()))
        response = Response(data)
        return response

    def expire_response_cache(self):
        obj_id = self.get_object_id()
        expire_cache_id = '{}_{}'.format(obj_id, '*')
        key = self.RESP_CACHE_KEY.format(expire_cache_id)
        cache.delete_pattern(key)

    def get_response_key(self):
        resp_cache_id = self.get_response_cache_id()
        key = self.RESP_CACHE_KEY.format(resp_cache_id)
        return key

    def set_response_to_cache(self, response):
        key = self.get_response_key()
        cache.set(key, response.data, self.CACHE_TIME)
        logger.debug("Set response to cache: {}".format(key))

    def get(self, request, *args, **kwargs):
        self.cache_policy = request.GET.get('cache_policy', '0')

        obj = self._get_object()
        if obj is None:
            logger.debug("Not get response from cache: obj is none")
            return super().get(request, *args, **kwargs)

        if AssetPermissionUtil.is_not_using_cache(self.cache_policy):
            logger.debug("Not get resp from cache: {}".format(self.cache_policy))
            return super().get(request, *args, **kwargs)
        elif AssetPermissionUtil.is_refresh_cache(self.cache_policy):
            logger.debug("Not get resp from cache: {}".format(self.cache_policy))
            self.expire_response_cache()

        logger.debug("Try get response from cache")
        resp = self.get_response_from_cache()
        if not resp:
            resp = super().get(request, *args, **kwargs)
            self.set_response_to_cache(resp)
        return resp


class GrantAssetsMixin:
    serializer_class = serializers.AssetGrantedSerializer

    def get_serializer(self, queryset, many=True):
        assets_ids = []
        system_users_ids = set()
        for asset in queryset:
            assets_ids.append(asset["id"])
            system_users_ids.update(set(asset["system_users"]))
        assets = Asset.objects.filter(id__in=assets_ids).only(
            *self.serializer_class.only_fields
        )
        assets_map = {asset.id: asset for asset in assets}
        system_users = SystemUser.objects.filter(id__in=system_users_ids).only(
            *self.serializer_class.system_user_only_field
        )
        system_users_map = {s.id: s for s in system_users}
        data = []
        for _asset in queryset:
            id = _asset["id"]
            asset = assets_map.get(id)
            if not asset:
                continue

            _system_users = _asset["system_users"]
            system_users_granted = []
            for sid, action in _system_users.items():
                system_user = system_users_map.get(sid)
                if not system_user:
                    continue
                system_user.actions = action
                system_users_granted.append(system_user)
            asset.system_users_granted = system_users_granted
            data.append(asset)
        return super().get_serializer(data, many=True)


class UserGrantedAssetsApi(UserPermissionCacheMixin, GrantAssetsMixin, ListAPIView):
    """
    用户授权的所有资产
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        user_id = self.kwargs.get('pk', '')
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = self.request.user
        return user

    def get_queryset(self):
        user = self.get_object()
        util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        queryset = util.get_assets()
        return queryset

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()


class NodesWithUngroupMixin:
    util = None

    def add_ungrouped_nodes(self, nodes_map):
        nodes_map[self.util.tree.ungrouped_key] = self.util.tree.ungrouped_node
        nodes_map[self.util.tree.empty_key] = self.util.tree.empty_node


class UserGrantedNodesApi(UserPermissionCacheMixin, NodesWithUngroupMixin, ListAPIView):
    """
    查询用户授权的所有节点的API
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    serializer_class = NodeSerializer
    pagination_class = LimitOffsetPagination
    only_fields = NodeSerializer.Meta.only_fields

    def get_object(self):
        user_id = self.kwargs.get('pk', '')
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = self.request.user
        return user

    def get_nodes(self, nodes_with_assets):
        node_keys = [n["key"] for n in nodes_with_assets]
        nodes = Node.objects.filter(key__in=node_keys).only(
            *self.only_fields
        )
        nodes_map = {n.key: n for n in nodes}
        self.add_ungrouped_nodes(nodes_map)

        _nodes = []
        for n in nodes_with_assets:
            key = n["key"]
            node = nodes_map.get(key)
            node._assets_amount = n["assets_amount"]
            _nodes.append(node)
        return _nodes

    def get_serializer(self, nodes_with_assets, many=True):
        nodes = self.get_nodes(nodes_with_assets)
        return super().get_serializer(nodes, many=True)

    def get_queryset(self):
        user = self.get_object()
        self.util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        nodes_with_assets = self.util.get_nodes_with_assets()
        return nodes_with_assets

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()


class UserGrantedNodesWithAssetsApi(UserPermissionCacheMixin, NodesWithUngroupMixin, ListAPIView):
    """
    用户授权的节点并带着节点下资产的api
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    serializer_class = serializers.NodeGrantedSerializer
    pagination_class = LimitOffsetPagination

    def get_object(self):
        user_id = self.kwargs.get('pk', '')
        if not user_id:
            user = self.request.user
        else:
            user = get_object_or_404(User, id=user_id)
        return user

    def get_queryset(self):
        user = self.get_object()
        self.util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        system_user_id = self.request.query_params.get('system_user')
        if system_user_id:
            self.util.filter_permissions(
                system_users=system_user_id
            )
        nodes = self.util.get_nodes_with_assets()
        return nodes

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()


class UserGrantedNodesAsTreeApi(UserGrantedNodesApi):
    serializer_class = TreeNodeSerializer
    only_fields = ParserNode.nodes_only_fields

    def get_serializer(self, nodes_with_assets, many=True):
        nodes = self.get_nodes(nodes_with_assets)
        queryset = []
        for node in nodes:
            data = ParserNode.parse_node_to_tree_node(node)
            queryset.append(data)
        return self.get_serializer_class()(queryset, many=many)


class UserGrantedNodesWithAssetsAsTreeApi(UserGrantedNodesWithAssetsApi):
    serializer_class = TreeNodeSerializer
    permission_classes = (IsOrgAdminOrAppUser,)
    system_user_id = None

    def get_maps(self, nodes):
        _nodes_keys = set()
        _assets_ids = set()
        _system_users_ids = set()
        for node in nodes:
            _nodes_keys.add(node["key"])
            _assets_ids.update(set(node["assets"].keys()))
            for _system_users_id in node["assets"].values():
                _system_users_ids.update(_system_users_id.keys())

        _nodes = Node.objects.filter(key__in=_nodes_keys).only(
            *ParserNode.nodes_only_fields
        )
        _assets = Asset.objects.filter(id__in=_assets_ids).only(
            *ParserNode.assets_only_fields
        )
        _system_users = SystemUser.objects.filter(
            id__in=_system_users_ids).only(
            *ParserNode.system_users_only_fields
        )
        _nodes_map = {n.key: n for n in _nodes}
        self.add_ungrouped_nodes(_nodes_map)
        _assets_map = {a.id: a for a in _assets}
        _system_users_map = {s.id: s for s in _system_users}
        return _nodes_map, _assets_map, _system_users_map

    def get_serializer(self, nodes, many=True):
        queryset = []
        print("Call get serialziers")
        print(len(nodes))
        now = time.clock()
        _nodes_map, _assets_map, _system_users_map = self.get_maps(nodes)

        for n in nodes:
            key = n["key"]
            node = _nodes_map.get(key)
            if not node:
                continue
            node._assets_amount = n["assets_amount"]
            data = ParserNode.parse_node_to_tree_node(node)
            queryset.append(data)
            for asset_id, system_users_ids_action in n["assets"].items():
                asset = _assets_map.get(asset_id)
                if not asset:
                    continue
                system_users = {
                    _system_users_map.get(system_user_id): action
                    for system_user_id, action in system_users_ids_action.items()
                }
                data = ParserNode.parse_asset_to_tree_node(node, asset, system_users)
                queryset.append(data)
        print("Call get sialzer using: {}".format(time.clock() - now))
        return super().get_serializer(queryset, many=many)


class UserGrantedNodeAssetsApi(UserPermissionCacheMixin, GrantAssetsMixin, ListAPIView):
    """
    查询用户授权的节点下的资产的api, 与上面api不同的是，只返回某个节点下的资产
    """
    permission_classes = (IsOrgAdminOrAppUser,)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        user_id = self.kwargs.get('pk', '')

        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = self.request.user
        return user

    def get_queryset(self):
        user = self.get_object()
        node_id = self.kwargs.get('node_id')
        util = AssetPermissionUtil(user, cache_policy=self.cache_policy)

        if str(node_id) == const.UNGROUPED_NODE_ID:
            key = util.tree.ungrouped_key
        elif str(node_id) == const.EMPTY_NODE_ID:
            key = util.tree.empty_key
        else:
            node = get_object_or_404(Node, id=node_id)
            key = node.key

        nodes = util.get_nodes_with_assets()
        for n in nodes:
            if n["key"] == key:
                assets = []
                for asset_id, system_users in n["assets"].items():
                    assets.append({"id": asset_id, "system_users": system_users})
                return assets
        return []

    def get_permissions(self):
        if self.kwargs.get('pk') is None:
            self.permission_classes = (IsValidUser,)
        return super().get_permissions()


class ValidateUserAssetPermissionApi(UserPermissionCacheMixin, APIView):
    permission_classes = (IsOrgAdminOrAppUser,)
    
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id', '')
        asset_id = request.query_params.get('asset_id', '')
        system_id = request.query_params.get('system_user_id', '')
        action_name = request.query_params.get('action_name', '')

        try:
            asset_id = uuid.UUID(asset_id)
            system_id = uuid.UUID(system_id)
        except ValueError:
            return Response({'msg': False}, status=403)

        user = get_object_or_404(User, id=user_id)
        util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        assets = util.get_assets()
        for asset in assets:
            if asset_id == asset["id"]:
                action = asset["system_users"].get(system_id)
                if action and action_name in Action.value_to_choices(action):
                    return Response({'msg': True}, status=200)
                break
        return Response({'msg': False}, status=403)


class GetUserAssetPermissionActionsApi(UserPermissionCacheMixin, RetrieveAPIView):
    permission_classes = (IsOrgAdminOrAppUser,)
    serializer_class = serializers.ActionsSerializer

    def get_object(self):
        user_id = self.request.query_params.get('user_id', '')
        asset_id = self.request.query_params.get('asset_id', '')
        system_id = self.request.query_params.get('system_user_id', '')

        user = get_object_or_404(User, id=user_id)
        asset = get_object_or_404(Asset, id=asset_id)
        su = get_object_or_404(SystemUser, id=system_id)

        util = AssetPermissionUtil(user, cache_policy=self.cache_policy)
        granted_assets = util.get_assets()
        granted_system_users = granted_assets.get(asset, {})

        _object = {}
        if su not in granted_system_users:
            _object['actions'] = 0
        else:
            _object['actions'] = granted_system_users[su]
        return _object
