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
