from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from math import radians, sin, cos, sqrt, atan2
from django.core.management.base import BaseCommand


# --- Early User System ---
# StoneWalker rewards the first N users (controlled by SHOP_VISIBLE_USER_THRESHOLD,
# default 1000) with free lifetime premium. This creates a sense of exclusivity and
# incentivizes early adoption before the paid shop/subscription goes live.
# The same threshold gates shop visibility, premium pricing display, and QR limits.

def get_user_number(user):
    """Get the registration order number for a user (1-based).
    Uses id__lte instead of date-based ordering because Django auto-increment IDs
    are monotonically increasing and survive deletions (gaps don't matter)."""
    return User.objects.filter(id__lte=user.id).count()


def is_early_user(user):
    """Check if a user registered within the first N users (threshold from settings).
    Used by: context processor (nav badge), email templates (welcome message),
    premium landing page (lifetime premium message), grant_early_premium()."""
    threshold = getattr(settings, 'SHOP_VISIBLE_USER_THRESHOLD', 1000)
    return get_user_number(user) <= threshold


def grant_early_premium(user):
    """Grant lifetime premium to an early user. Returns the Subscription or None.
    Called during account activation (ActivateView) so the premium is granted
    only after email verification, not at signup. This prevents throwaway accounts
    from consuming early-user slots. Idempotent: safe to call multiple times."""
    if not is_early_user(user):
        return None
    sub, created = Subscription.objects.get_or_create(
        user=user,
        defaults={
            'plan': 'lifetime',
            'status': 'active',
        }
    )
    # If the user already had a lapsed/canceled subscription, upgrade it
    if not created and not sub.grants_premium:
        sub.plan = 'lifetime'
        sub.status = 'active'
        sub.save()
    return sub


class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Social media profile connections
    facebook_url = models.URLField(blank=True, default='')
    instagram_handle = models.CharField(max_length=50, blank=True, default='')
    twitter_handle = models.CharField(max_length=50, blank=True, default='')
    mastodon_handle = models.CharField(max_length=100, blank=True, default='')
    tiktok_handle = models.CharField(max_length=50, blank=True, default='')

    def has_picture(self):
        return self.profile_picture and hasattr(self.profile_picture, "url")

    def get_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return settings.STATIC_URL + 'user_picture.png'

    def has_social_links(self):
        return any([
            self.facebook_url, self.instagram_handle, self.twitter_handle,
            self.mastodon_handle, self.tiktok_handle,
        ])

    def get_share_handle(self):
        """Return the best social handle for share text mentions."""
        if self.twitter_handle:
            handle = self.twitter_handle.lstrip('@')
            return f'@{handle}'
        if self.instagram_handle:
            handle = self.instagram_handle.lstrip('@')
            return f'@{handle}'
        return self.user.username

    @property
    def is_premium(self):
        """Check if user has an active premium subscription."""
        try:
            return self.user.subscription.grants_premium
        except Subscription.DoesNotExist:
            return False

    def __str__(self):
        return f"Profile of {self.user.username}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class EmailAddressState(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='email_state')
    email = models.EmailField(unique=True)
    is_confirmed = models.BooleanField(default=False)
    old_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.email} ({'confirmed' if self.is_confirmed else 'pending'})"


class EmailChangeAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_change_attempts')
    email = models.EmailField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} tried {self.email} at {self.attempted_at}"


class TermsAcceptance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='terms_acceptance')
    accepted_at = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=10, default='1.0')

    def __str__(self):
        return f"{self.user.username} accepted terms v{self.version} at {self.accepted_at}"


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_prefs')
    stone_scanned = models.BooleanField(default=True)
    stone_moved = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification prefs for {self.user.username}"


class Subscription(models.Model):
    """Tracks premium supporter subscriptions via Stripe recurring billing."""
    # 'lifetime' plan is granted automatically to early users (first N registrations)
    # and has no Stripe subscription — it's a local-only status that bypasses billing.
    PLAN_CHOICES = [
        ('monthly', 'Monthly ($3.99/mo)'),
        ('yearly', 'Yearly ($29.99/yr)'),
        ('lifetime', 'Lifetime (Early Supporter)'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('trialing', 'Trialing'),
        ('incomplete', 'Incomplete'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default='')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription grants premium access."""
        return self.status in ('active', 'trialing')

    @property
    def is_canceled_but_active(self):
        """Subscription canceled but still in paid period."""
        if self.status == 'canceled' and self.current_period_end:
            return timezone.now() < self.current_period_end
        return False

    @property
    def grants_premium(self):
        """Whether this subscription currently grants premium features."""
        return self.is_active or self.is_canceled_but_active

    class Meta:
        ordering = ['-created_at']
