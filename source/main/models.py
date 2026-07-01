from django.db import models
from django.conf import settings
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

    # Language for PDF generation (captured at checkout time)
    language = models.CharField(max_length=10, default='en')

    def __str__(self):
        return f"{self.get_pack_type_display()} - {self.get_status_display()} ({self.id})"

    class Meta:
        ordering = ['-created_at']


class Stone(models.Model):
    STATUS_CHOICES = [
        ('unclaimed', 'Unclaimed'),  # Pre-generated, no owner yet
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('wandering', 'Wandering'),
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
    wandering_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True, help_text='When this stone was claimed by a user')
    stone_number = models.PositiveIntegerField(unique=True, null=True, blank=True, help_text='Sequential stone number, auto-assigned on creation')

    def __str__(self):
        return f"{self.PK_stone} ({self.status})"

    def save(self, *args, **kwargs):
        if self.stone_number is None:
            max_num = Stone.objects.aggregate(models.Max('stone_number'))['stone_number__max']
            self.stone_number = (max_num or 0) + 1
            # Ensure stone_number is persisted even when update_fields is used
            if 'update_fields' in kwargs and kwargs['update_fields'] is not None:
                kwargs['update_fields'] = list(kwargs['update_fields']) + ['stone_number']
        super().save(*args, **kwargs)

    def get_stone_number(self):
        """Get this stone's sequential number."""
        return self.stone_number

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
    
    def can_start_wandering(self):
        """Check if stone can start wandering (sealed via QR scan)"""
        return self.status in ('draft', 'published')

    def start_wandering(self):
        """Transition stone to wandering status (sealed via QR scan)"""
        if self.can_start_wandering():
            if self.status == 'draft':
                self.status = 'wandering'
            else:
                self.status = 'wandering'
            self.wandering_at = timezone.now()
            self.save()
            return True
        return False

    def can_download_qr(self):
        """QR download is available for unclaimed (owned via pack) and
        draft/published stones — but not once wandering (already sealed).
        Lets an owner download a bought code's QR without claiming it."""
        return self.status in ('unclaimed', 'draft', 'published')

    def can_download_certificate(self):
        """Certificate download is only available for wandering stones"""
        return self.status == 'wandering'

    def publish(self):
        """Publish the stone (make it visible on map)"""
        if self.can_be_published():
            self.status = 'published'
            self.save()
            return True
        return False
    
    # Production domain for QR codes
    PRODUCTION_DOMAIN = 'stonewalker.org'

    def get_qr_url(self):
        """Get the QR code URL for this stone - always uses production domain"""
        if self.stone_number is None:
            self.save()  # triggers auto-assignment
        production_url = f'https://{self.PRODUCTION_DOMAIN}/stone-link/{self.stone_number}/?key={self.uuid}'

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

    # --- QR free allowance + dynamic pricing ---
    # Non-premium users may hold up to FREE_UNCLAIMED_CAP unclaimed codes for
    # free. Beyond that they pay per code (a soft line — no hard block). Premium
    # supporters have no cap and never pay. Ownership of an unclaimed code is via
    # its pack (FK_pack.FK_user), since unclaimed stones have FK_user=None.
    FREE_UNCLAIMED_CAP = 30
    PRICE_PER_CODE_CENTS = 50  # $0.50 per QR code beyond the free allowance

    @classmethod
    def unclaimed_count(cls, user):
        """Number of unclaimed codes a user currently holds (across their packs)."""
        return cls.objects.filter(FK_pack__FK_user=user, status='unclaimed').count()

    @classmethod
    def user_has_unclaimed_qr(cls, user):
        """Whether the user holds any unclaimed QR codes (via their packs)."""
        return cls.objects.filter(FK_pack__FK_user=user, status='unclaimed').exists()

    @classmethod
    def _user_is_premium(cls, user):
        try:
            return bool(user.profile.is_premium)
        except Exception:
            return False

    @classmethod
    def remaining_free_allowance(cls, user):
        """Free unclaimed codes still available, or None if unlimited (premium)."""
        if cls._user_is_premium(user):
            return None
        return max(0, cls.FREE_UNCLAIMED_CAP - cls.unclaimed_count(user))

    @classmethod
    def pack_is_free_for_user(cls, user, pack_size=1):
        """The dynamic-pricing decision. A pack is free if the user is premium,
        or if it fits within the free allowance (current unclaimed + pack_size
        <= FREE_UNCLAIMED_CAP). Otherwise the whole pack costs its listed price."""
        if cls._user_is_premium(user):
            return True
        return cls.unclaimed_count(user) + pack_size <= cls.FREE_UNCLAIMED_CAP

    @classmethod
    def user_can_get_new_qr(cls, user, pack_size=1):
        """True when the user can get this pack FOR FREE (within allowance or
        premium). Non-premium users beyond the allowance are not blocked — they
        pay — so callers use this to choose the free vs paid path, not to gate."""
        return cls.pack_is_free_for_user(user, pack_size)
    
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
    # False while a find submitted by an unconfirmed (email-first) finder is on
    # hold. Pending moves are hidden from the public map and excluded from
    # distance until the finder confirms their email. Existing rows default True.
    is_confirmed = models.BooleanField(default=True)

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
    # Only confirmed moves count — a pending (unconfirmed) find must not inflate
    # distance before the finder confirms their email.
    moves = list(stone.moves.filter(is_confirmed=True).order_by('timestamp').all())
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


def confirm_pending_finds(user):
    """Release a user's held (email-first) finds once they confirm their email:
    flip their pending moves to confirmed and recompute each affected stone's
    distance. Returns the number of finds released. Idempotent."""
    pending = list(
        StoneMove.objects.filter(FK_user=user, is_confirmed=False).select_related('FK_stone')
    )
    if not pending:
        return 0
    StoneMove.objects.filter(FK_user=user, is_confirmed=False).update(is_confirmed=True)
    for stone in {m.FK_stone for m in pending}:
        stone.distance_km = calculate_stone_distance(stone)
        stone.save(update_fields=['distance_km'])
    return len(pending)

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