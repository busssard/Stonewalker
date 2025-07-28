from django.core.management.base import BaseCommand
from main.models import Stone, calculate_stone_distance

class Command(BaseCommand):
    help = 'Recalculate and update the distance_km field for all stones.'

    def handle(self, *args, **options):
        updated = 0
        for stone in Stone.objects.all():
            distance = calculate_stone_distance(stone)
            stone.distance_km = distance
            stone.save()
            self.stdout.write(self.style.SUCCESS(f"{stone.PK_stone}: {distance} km"))
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} stones.")) 