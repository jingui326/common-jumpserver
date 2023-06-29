# -*- coding: utf-8 -*-
#
import os
import uuid

from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny

from common.permissions import IsValidUser
from common.views.http import HttpResponseTemporaryRedirect
from common.utils import get_logger, FlashMessageUtil, bulk_get
from common.const import KEY_CACHE_RESOURCE_IDS

__all__ = [
    'LogTailApi', 'ResourcesIDCacheApi', 'FlashMessageMsgApi'
]

logger = get_logger(__file__)


class OutputSerializer(serializers.Serializer):
    output = serializers.CharField()
    is_end = serializers.BooleanField()
    mark = serializers.CharField()


class LogTailApi(generics.RetrieveAPIView):
    permission_classes = (IsValidUser,)
    buff_size = 1024 * 10
    serializer_class = OutputSerializer
    end = False
    mark = ''
    log_path = ''

    def is_file_finish_write(self):
        return True

    def get_log_path(self):
        raise NotImplementedError()

    def get_no_file_message(self, request):
        return 'Not found the log'

    def filter_line(self, line):
        """
        过滤行，可能替换一些信息
        :param line:
        :return:
        """
        return line

    def read_from_file(self):
        with open(self.log_path, 'rt', encoding='utf8') as f:
            offset = cache.get(self.mark, 0)
            f.seek(offset)
            data = f.read(self.buff_size).replace('\n', '\r\n')

            new_mark = str(uuid.uuid4())
            cache.set(new_mark, f.tell(), 5)

            if data == '' and self.is_file_finish_write():
                self.end = True
            _data = ''
            for line in data.split('\r\n'):
                new_line = self.filter_line(line)
                if line == '':
                    continue
                _data += new_line + '\r\n'
            return _data, self.end, new_mark

    def get(self, request, *args, **kwargs):
        self.mark = request.query_params.get("mark") or str(uuid.uuid4())
        self.log_path = self.get_log_path()

        if not self.log_path or not os.path.isfile(self.log_path):
            msg = self.get_no_file_message(self.request)
            return Response({"data": msg}, status=200)

        data, end, new_mark = self.read_from_file()
        return Response({"data": data, 'end': end, 'mark': new_mark})


class ResourcesIDCacheApi(APIView):
    permission_classes = (IsValidUser,)

    def post(self, request, *args, **kwargs):
        spm = str(uuid.uuid4())
        resources = request.data.get('resources')
        if resources is not None:
            cache_key = KEY_CACHE_RESOURCE_IDS.format(spm)
            cache.set(cache_key, resources, 300)
        return Response({'spm': spm})


@csrf_exempt
def redirect_plural_name_api(request, *args, **kwargs):
    resource = kwargs.get("resource", "")
    org_full_path = request.get_full_path()
    full_path = org_full_path.replace(resource, resource + "s", 1)
    logger.debug("Redirect {} => {}".format(org_full_path, full_path))
    return HttpResponseTemporaryRedirect(full_path)


class FlashMessageMsgApi(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request, *args, **kwargs):
        code = request.GET.get('code')
        if not code:
            return Response(data={'error': 'Not found the code'}, status=404)

        message_data = FlashMessageUtil.get_message_by_code(code)
        if not message_data:
            return Response(data={'error': 'Message code error'}, status=400)

        items = ('title', 'message', 'error', 'redirect_url', 'confirm_button', 'cancel_url')
        title, msg, error, redirect_url, confirm_btn, cancel_url = bulk_get(message_data, items)

        interval = message_data.get('interval', 3)
        auto_redirect = message_data.get('auto_redirect', True)
        has_cancel = message_data.get('has_cancel', False)
        context = {
            'title': title,
            'message': msg,
            'error': error,
            'interval': interval,
            'redirect_url': redirect_url,
            'auto_redirect': auto_redirect,
            'confirm_button': confirm_btn,
            'has_cancel': has_cancel,
            'cancel_url': cancel_url,
        }
        return Response(data=context, status=200)
