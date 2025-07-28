from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from math import radians, sin, cos, sqrt, atan2
from django.core.management.base import BaseCommand

def validate_no_whitespace(value):
    if re.search(r'\s', value):
        raise ValidationError('Stone name cannot contain whitespace.')

class Stone(models.Model):
    PK_stone = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_no_whitespace],
        primary_key=True
    )
    description = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    FK_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stones')
    image = models.ImageField(upload_to='stones/', blank=True, null=True)
    color = models.CharField(max_length=7, default='#4CAF50')
    shape = models.CharField(max_length=20, default='circle')
    distance_km = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.PK_stone}"

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