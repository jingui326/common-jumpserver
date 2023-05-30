# coding:utf-8
#
from django.urls import path
from rest_framework.routers import DefaultRouter

from .. import api

app_name = 'authentication'
router = DefaultRouter()
router.register('access-keys', api.AccessKeyViewSet, 'access-key')
router.register('sso', api.SSOViewSet, 'sso')
router.register('temp-tokens', api.TempTokenViewSet, 'temp-token')
router.register('connection-token', api.ConnectionTokenViewSet, 'connection-token')
router.register('super-connection-token', api.SuperConnectionTokenViewSet, 'super-connection-token')


urlpatterns = [
    path('wecom/qr/unbind/', api.WeComQRUnBindForUserApi.as_view(), name='wecom-qr-unbind'),
    path('wecom/qr/unbind/<uuid:user_id>/', api.WeComQRUnBindForAdminApi.as_view(), name='wecom-qr-unbind-for-admin'),

    path('dingtalk/qr/unbind/', api.DingTalkQRUnBindForUserApi.as_view(), name='dingtalk-qr-unbind'),
    path('dingtalk/qr/unbind/<uuid:user_id>/', api.DingTalkQRUnBindForAdminApi.as_view(), name='dingtalk-qr-unbind-for-admin'),

    path('feishu/qr/unbind/', api.FeiShuQRUnBindForUserApi.as_view(), name='feishu-qr-unbind'),
    path('feishu/qr/unbind/<uuid:user_id>/', api.FeiShuQRUnBindForAdminApi.as_view(), name='feishu-qr-unbind-for-admin'),
    path('feishu/event/subscription/callback/', api.FeiShuEventSubscriptionCallback.as_view(), name='feishu-event-subscription-callback'),

    path('auth/', api.TokenCreateApi.as_view(), name='user-auth'),
    path('confirm/', api.ConfirmApi.as_view(), name='user-confirm'),
    path('confirm-oauth/', api.ConfirmBindORUNBindOAuth.as_view(), name='confirm-oauth'),
    path('tokens/', api.TokenCreateApi.as_view(), name='auth-token'),
    path('mfa/settings/', api.MFASettingsApi.as_view(), name='mfa-settings'),
    path('mfa/verify/', api.MFAChallengeVerifyApi.as_view(), name='mfa-verify'),
    path('mfa/challenge/', api.MFAChallengeVerifyApi.as_view(), name='mfa-challenge'),
    path('mfa/select/', api.MFASendCodeApi.as_view(), name='mfa-select'),
    path('mfa/send-code/', api.MFASendCodeApi.as_view(), name='mfa-send-code'),
    path('password/reset-code/', api.UserResetPasswordSendCodeApi.as_view(), name='reset-password-code'),
    path('password/verify/', api.UserPasswordVerifyApi.as_view(), name='user-password-verify'),
    path('login-confirm-ticket/status/', api.TicketStatusApi.as_view(), name='login-confirm-ticket-status'),

    path('password/forget/previewing/', api.ForgetPasswordPreviewingApi.as_view(), name='forgot-previewing'),
    path('password/forget/auth/', api.ForgetPasswordAuthApi.as_view(), name='forgot-auth'),
    path('login/', api.LoginApi.as_view(), name='login'),
]

urlpatterns += router.urls
