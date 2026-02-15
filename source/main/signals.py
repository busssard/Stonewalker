from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='main.StoneMove')
def notify_stone_owner_on_move(sender, instance, created, **kwargs):
    """Send email notification to stone owner when their stone is scanned/moved."""
    if not created:
        return

    stone = instance.FK_stone
    mover = instance.FK_user
    owner = stone.FK_user

    # Skip if mover is the owner or stone has no owner
    if not owner or mover == owner:
        return

    # Check notification preferences
    try:
        prefs = owner.notification_prefs
    except Exception:
        # No prefs set, default to sending
        prefs = None

    if prefs and not prefs.stone_scanned:
        return

    # Send email
    try:
        context = {
            'subject': f'Your stone "{stone.PK_stone}" was scanned!',
            'stone': stone,
            'mover': mover,
            'owner': owner,
            'move': instance,
        }
        html_content = render_to_string('accounts/emails/stone_scanned.html', context)
        text_content = render_to_string('accounts/emails/stone_scanned.txt', context)

        msg = EmailMultiAlternatives(
            context['subject'],
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [owner.email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
    except Exception as e:
        logger.error(f'Failed to send stone scan notification to {owner.email}: {e}')
