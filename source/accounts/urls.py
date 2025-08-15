from django.urls import path
from django.conf import settings

from .views import (
    LogInView, ResendActivationCodeView, RemindUsernameView, SignUpView, ActivateView, LogOutView,
    ChangeProfileView, ChangeEmailActivateView, ResendEmailActivationView, CancelEmailChangeView,
    RestorePasswordView, RestorePasswordDoneView, RestorePasswordConfirmView, LogOutConfirmView,
    check_username,
)

app_name = 'accounts'

urlpatterns = [
    path('log-in/', LogInView.as_view(), name='log_in'),
    path('log-out/confirm/', LogOutConfirmView.as_view(), name='log_out_confirm'),
    path('log-out/', LogOutView.as_view(), name='log_out'),

    path('resend/activation-code/', ResendActivationCodeView.as_view(), name='resend_activation_code'),

    path('sign-up/', SignUpView.as_view(), name='sign_up'),
    path('activate/<code>/', ActivateView.as_view(), name='activate'),

    path('restore/password/', RestorePasswordView.as_view(), name='restore_password'),
    path('restore/password/done/', RestorePasswordDoneView.as_view(), name='restore_password_done'),
    path('restore/<uidb64>/<token>/', RestorePasswordConfirmView.as_view(), name='restore_password_confirm'),

    path('remind/username/', RemindUsernameView.as_view(), name='remind_username'),

    path('change/profile/', ChangeProfileView.as_view(), name='change_profile'),
    path('change/email/<code>/', ChangeEmailActivateView.as_view(), name='change_email_activation'),
    path('resend-email-activation/', ResendEmailActivationView.as_view(), name='resend_email_activation'),
    path('cancel-email-change/', CancelEmailChangeView.as_view(), name='cancel_email_change'),
    path('api/check_username/', check_username, name='check_username'),

] 