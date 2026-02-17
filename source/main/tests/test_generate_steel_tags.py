"""
Tests for the generate_steel_tags management command
"""

import csv
import tempfile
import os

from django.test import TestCase
from django.core.management import call_command

from ..models import Stone


class GenerateSteelTagsTests(TestCase):
    """Test the generate_steel_tags management command"""

    def test_creates_correct_number_of_stones(self):
        """Run command with --count 5, verify 5 unclaimed stones created"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            call_command('generate_steel_tags', count=5, output=output_path)
            self.assertEqual(Stone.objects.filter(status='unclaimed').count(), 5)
        finally:
            os.unlink(output_path)

    def test_csv_output_has_correct_columns(self):
        """Verify CSV has stone_number,uuid,qr_url header"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            call_command('generate_steel_tags', count=2, output=output_path)
            with open(output_path) as f:
                reader = csv.reader(f)
                header = next(reader)
            self.assertEqual(header, ['stone_number', 'uuid', 'qr_url'])
        finally:
            os.unlink(output_path)

    def test_csv_urls_are_production(self):
        """Verify URLs match https://stonewalker.org/stone-link/{uuid}/"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            call_command('generate_steel_tags', count=3, output=output_path)
            with open(output_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    expected = f"https://stonewalker.org/stone-link/{row['uuid']}/"
                    self.assertEqual(row['qr_url'], expected)
        finally:
            os.unlink(output_path)

    def test_stones_are_unclaimed(self):
        """All created stones have status='unclaimed' and FK_user=None"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            call_command('generate_steel_tags', count=4, output=output_path)
            for stone in Stone.objects.all():
                self.assertEqual(stone.status, 'unclaimed')
                self.assertIsNone(stone.FK_user)
        finally:
            os.unlink(output_path)

    def test_default_count(self):
        """Without --count, defaults to 500"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            call_command('generate_steel_tags', output=output_path)
            self.assertEqual(Stone.objects.filter(status='unclaimed').count(), 500)
        finally:
            os.unlink(output_path)
