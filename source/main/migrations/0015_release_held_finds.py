"""Release finds that were held waiting for the finder's email confirmation.

Finds on sent-off (wandering) stones now go on the map immediately; this puts
the existing held ones there too and recomputes each affected stone's
distance (same rules as main.models.calculate_stone_distance, inlined because
migrations must use historical models).
"""
from math import atan2, cos, radians, sin, sqrt

from django.db import migrations


def _haversine_km(a, b):
    lat1, lon1 = a
    lat2, lon2 = b
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    h = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371 * 2 * atan2(sqrt(h), sqrt(1 - h))


def release_held_finds(apps, schema_editor):
    Stone = apps.get_model('main', 'Stone')
    StoneMove = apps.get_model('main', 'StoneMove')

    held = StoneMove.objects.filter(is_confirmed=False, FK_stone__status='wandering')
    stone_ids = set(held.values_list('FK_stone_id', flat=True))
    held.update(is_confirmed=True)

    for stone in Stone.objects.filter(pk__in=stone_ids):
        points = [
            (m.latitude, m.longitude)
            for m in StoneMove.objects.filter(FK_stone=stone, is_confirmed=True).order_by('timestamp')
        ]
        if (points and stone.stone_type == 'hidden'
                and stone.hide_latitude is not None and stone.hide_longitude is not None):
            points.insert(0, (stone.hide_latitude, stone.hide_longitude))
        total = sum(_haversine_km(points[i - 1], points[i]) for i in range(1, len(points)))
        stone.distance_km = round(total, 1)
        stone.save(update_fields=['distance_km'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_stone_hide_location'),
    ]

    operations = [
        migrations.RunPython(release_held_finds, migrations.RunPython.noop),
    ]
