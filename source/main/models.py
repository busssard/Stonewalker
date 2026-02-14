from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from math import radians, sin, cos, sqrt, atan2
from django.core.management.base import BaseCommand
import uuid
from datetime import timedelta
from django.utils import timezone

def validate_no_whitespace(value):
    if re.search(r'\s', value):
        raise ValidationError('Stone name cannot contain whitespace.')


class QRPack(models.Model):
    """Tracks purchased QR code packs from the shop"""
    PACK_TYPES = [
        ('free_single', 'Free Single QR'),
        ('paid_10pack', 'Paid 10-Pack'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('fulfilled', 'Fulfilled'),
        ('failed', 'Payment Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FK_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='qr_packs',
        null=True,
        blank=True,
        help_text='User who purchased the pack'
    )
    pack_type = models.CharField(max_length=20, choices=PACK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    # Pricing
    price_cents = models.IntegerField(default=0, help_text='Price in cents')
    currency = models.CharField(max_length=3, default='USD')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)

    # Download tracking
    pdf_generated = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_pack_type_display()} - {self.get_status_display()} ({self.id})"

    class Meta:
        ordering = ['-created_at']


class Stone(models.Model):
    STATUS_CHOICES = [
        ('unclaimed', 'Unclaimed'),  # Pre-generated, no owner yet
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('sent_off', 'Sent Off'),
    ]

    PK_stone = models.CharField(
        max_length=50,  # Increased for temporary unclaimed names like UNCLAIMED-ABC12345
        unique=True,
        validators=[validate_no_whitespace],
        primary_key=True
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    FK_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stones',
        null=True,  # Nullable for unclaimed stones
        blank=True
    )
    FK_pack = models.ForeignKey(
        QRPack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stones',
        help_text='QR pack this stone belongs to (if from shop)'
    )
    image = models.ImageField(upload_to='stones/', blank=True, null=True)
    color = models.CharField(max_length=7, default='#4CAF50')
    shape = models.CharField(max_length=20, default='circle')
    distance_km = models.FloatField(default=0.0)
    stone_type = models.CharField(max_length=20, default='hidden', choices=[
        ('hidden', 'Hidden'),
        ('hunted', 'Hunted'),
    ])
    status = models.CharField(max_length=20, default='draft', choices=STATUS_CHOICES)
    qr_code_url = models.URLField(blank=True, help_text='Persistent QR code URL')
    sent_off_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True, help_text='When this stone was claimed by a user')

    def __str__(self):
        return f"{self.PK_stone} ({self.status})"

    def get_stone_number(self):
        """Get this stone's sequential number based on creation order.
        Returns the 1-based position among all stones ordered by created_at."""
        if not self.created_at:
            return None
        count = Stone.objects.filter(created_at__lt=self.created_at).count()
        return count + 1

    def is_unclaimed(self):
        """Check if stone is unclaimed and available to be claimed"""
        return self.status == 'unclaimed'

    def can_be_claimed(self):
        """Check if stone can be claimed by a user"""
        return self.status == 'unclaimed' and self.FK_user is None

    def claim(self, user, new_name, description='', image=None):
        """Claim this stone for a user"""
        if not self.can_be_claimed():
            return False

        self.PK_stone = new_name
        self.FK_user = user
        self.status = 'draft'
        self.claimed_at = timezone.now()
        if description:
            self.description = description[:500]
        if image:
            self.image = image
        self.save()
        return True

    def can_be_edited(self):
        """Check if stone can be edited (only drafts can be edited)"""
        return self.status == 'draft'

    def can_be_published(self):
        """Check if stone can be published"""
        return self.status == 'draft'
    
    def can_be_sent_off(self):
        """Check if stone can be sent off"""
        return self.status == 'published'
    
    def publish(self):
        """Publish the stone (make it visible on map)"""
        if self.can_be_published():
            self.status = 'published'
            self.save()
            return True
        return False
    
    def send_off(self):
        """Send off the stone (finalize it, no more editing)"""
        if self.can_be_sent_off():
            self.status = 'sent_off'
            self.sent_off_at = timezone.now()
            self.save()
            return True
        return False
    
    # Production domain for QR codes
    PRODUCTION_DOMAIN = 'stonewalker.org'

    def get_qr_url(self):
        """Get the QR code URL for this stone - always uses production domain"""
        # Always generate the production URL for QR codes
        production_url = f'https://{self.PRODUCTION_DOMAIN}/stone-link/{self.uuid}/'

        # Update stored URL if different
        if self.qr_code_url != production_url:
            self.qr_code_url = production_url
            self.save(update_fields=['qr_code_url'])

        return self.qr_code_url
    
    @classmethod
    def user_can_create_stone(cls, user):
        """Check if user can create a new stone (non-premium users limited to 1 draft)"""
        if hasattr(user, 'is_premium') and user.is_premium:
            return True
        # Non-premium users can only have one draft stone at a time
        draft_count = cls.objects.filter(FK_user=user, status='draft').count()
        return draft_count == 0
    
    @classmethod
    def get_user_draft_stone(cls, user):
        """Get user's current draft stone if any"""
        return cls.objects.filter(FK_user=user, status='draft').first()

class StoneMove(models.Model):
    FK_stone = models.ForeignKey(Stone, on_delete=models.CASCADE, to_field='PK_stone', related_name='moves')
    FK_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stone_moves')
    image = models.ImageField(upload_to='stonemoves/', blank=True, null=True)
    comment = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move for {self.FK_stone.PK_stone} at {self.timestamp}"

class StoneScanAttempt(models.Model):
    """Track scan attempts to enforce one-week blackout period"""
    FK_stone = models.ForeignKey(Stone, on_delete=models.CASCADE, related_name='scan_attempts')
    FK_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stone_scan_attempts')
    scan_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['FK_stone', 'FK_user']
        indexes = [
            models.Index(fields=['FK_stone', 'FK_user', 'scan_time']),
        ]
    
    def __str__(self):
        return f"Scan attempt for {self.FK_stone.PK_stone} by {self.FK_user.username} at {self.scan_time}"
    
    @classmethod
    def can_scan_again(cls, stone, user):
        """Check if user can scan this stone again (one week blackout)"""
        one_week_ago = timezone.now() - timedelta(weeks=1)
        recent_attempt = cls.objects.filter(
            FK_stone=stone,
            FK_user=user,
            scan_time__gte=one_week_ago
        ).first()
        return recent_attempt is None
    
    @classmethod
    def record_scan_attempt(cls, stone, user, request=None):
        """Record a scan attempt for the stone"""
        attempt, created = cls.objects.get_or_create(
            FK_stone=stone,
            FK_user=user,
            defaults={
                'ip_address': request.META.get('REMOTE_ADDR') if request else None,
                'user_agent': request.META.get('HTTP_USER_AGENT', '') if request else '',
            }
        )
        if not created:
            # Update existing record with new scan time
            attempt.scan_time = timezone.now()
            if request:
                attempt.ip_address = request.META.get('REMOTE_ADDR')
                attempt.user_agent = request.META.get('HTTP_USER_AGENT', '')
            attempt.save()
        return attempt

def calculate_stone_distance(stone):
    moves = list(stone.moves.order_by('timestamp').all())
    total_distance = 0.0
    for i in range(1, len(moves)):
        lat1, lon1 = moves[i-1].latitude, moves[i-1].longitude
        lat2, lon2 = moves[i].latitude, moves[i].longitude
        if None not in (lat1, lon1, lat2, lon2):
            R = 6371
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            total_distance += R * c
    return round(total_distance, 1)

class Command(BaseCommand):
    help = 'Remove image from first StoneMove if it matches the Stone image (retroactive fix for hunted stones)'

    def handle(self, *args, **options):
        from main.models import Stone, StoneMove
        count = 0
        for stone in Stone.objects.all():
            first_move = stone.moves.order_by('timestamp').first()
            if first_move and first_move.image and stone.image and first_move.image.name == stone.image.name:
                first_move.image = None
                first_move.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Removed image from {count} StoneMove entries.')) 