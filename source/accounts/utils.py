from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    text_content = render_to_string(f'accounts/emails/{template}.txt', context)

    msg = EmailMultiAlternatives(context['subject'], text_content, settings.DEFAULT_FROM_EMAIL, [to])
    msg.attach_alternative(html_content, 'text/html')
    
    try:
        msg.send()
        return True
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False


def send_activation_email(request, email, code, user=None):
    """Send account activation email. When user is provided, the email includes
    the user's registration number ("You are member #42!") and, for early users,
    a message about lifetime premium. This creates excitement and a sense of
    belonging from the very first interaction."""
    from django.contrib.auth.models import User

    context = {
        'subject': _('Profile activation'),
        'uri': request.build_absolute_uri(reverse('accounts:activate', kwargs={'code': code})),
    }

    if user is not None:
        from .models import get_user_number, is_early_user
        user_number = get_user_number(user)
        context['user_number'] = user_number
        context['is_early_user'] = is_early_user(user)

    return send_mail(email, 'activate_profile', context)


def send_activation_change_email(request, email, code):
    context = {
        'subject': _('Change email'),
        'uri': request.build_absolute_uri(reverse('accounts:change_email_activation', kwargs={'code': code})),
    }

    return send_mail(email, 'change_email', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': _('Restore password'),
        'uri': request.build_absolute_uri(
            reverse('accounts:restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    send_mail(email, 'restore_password_email', context)


def send_forgotten_username_email(email, username):
    context = {
        'subject': _('Your username'),
        'username': username,
    }

    send_mail(email, 'forgotten_username', context)
