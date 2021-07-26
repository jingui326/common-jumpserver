# coding:utf-8
#
from django.urls import path
from rest_framework_bulk.routes import BulkRouter
from .. import api


app_name = 'applications'


router = BulkRouter()
router.register(r'applications', api.ApplicationViewSet, 'application')


urlpatterns = [
    path('remote-apps/<uuid:pk>/connection-info/', api.RemoteAppConnectionInfoApi.as_view(), name='remote-app-connection-info'),
    path('accounts/', api.ApplicationAccountListApi.as_view(), name='application-account'),
    path('account-secrets/', api.ApplicationAccountAuthInfoListApi.as_view(), name='application-account-secret')
]


urlpatterns += router.urls
