from django.core.management.base import BaseCommand
from main.models import Stone

class Command(BaseCommand):
    help = 'Remove image from first StoneMove if both the Stone and the first StoneMove have an image (regardless of filename)'

    def handle(self, *args, **options):
        count = 0
        for stone in Stone.objects.all():
            first_move = stone.moves.order_by('timestamp').first()
            if first_move and first_move.image and stone.image:
                first_move.image = None
                first_move.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Removed image from {count} StoneMove entries.')) 