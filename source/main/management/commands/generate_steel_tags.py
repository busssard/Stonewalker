import csv
import uuid as uuid_lib

from django.core.management.base import BaseCommand

from main.models import Stone


class Command(BaseCommand):
    help = 'Bulk-create unclaimed stones and export a CSV with their QR URLs for steel tag engraving.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=500,
            help='Number of unclaimed stones to create (default: 500)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='steel_tags.csv',
            help='CSV output file path (default: steel_tags.csv)',
        )

    def handle(self, *args, **options):
        count = options['count']
        output = options['output']

        stones = []
        for i in range(count):
            temp_name = f'UNCLAIMED-{uuid_lib.uuid4().hex[:8].upper()}'
            stone = Stone.objects.create(
                PK_stone=temp_name,
                FK_user=None,
                FK_pack=None,
                status='unclaimed',
            )
            stones.append(stone)

        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['stone_number', 'uuid', 'qr_url'])
            for i, stone in enumerate(stones, start=1):
                writer.writerow([i, stone.uuid, stone.get_qr_url()])

        self.stdout.write(self.style.SUCCESS(
            f'Created {count} unclaimed stones. CSV written to {output}'
        ))
