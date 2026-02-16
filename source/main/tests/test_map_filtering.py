from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import Stone, StoneMove
import json


class MapFilteringTests(TestCase):
    """Tests for map filtering functionality"""

    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create hidden stone with moves
        self.hidden_stone = Stone.objects.create(
            PK_stone='HiddenStone',
            FK_user=self.user,
            stone_type='hidden',
            status='sent_off',
            color='#FF0000'
        )
        StoneMove.objects.create(
            FK_stone=self.hidden_stone,
            FK_user=self.user,
            latitude=40.7128,
            longitude=-74.0060
        )

        # Create hunted stone with moves
        self.hunted_stone = Stone.objects.create(
            PK_stone='HuntedStone',
            FK_user=self.user,
            stone_type='hunted',
            status='sent_off',
            color='#00FF00'
        )
        StoneMove.objects.create(
            FK_stone=self.hunted_stone,
            FK_user=self.user,
            latitude=51.5074,
            longitude=-0.1278
        )

    def test_stonewalker_page_includes_filter_controls(self):
        """Stonewalker page should include filter controls"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)

        # Check for filter checkboxes
        self.assertContains(response, 'id="filter-all"')
        self.assertContains(response, 'id="filter-hidden"')
        self.assertContains(response, 'id="filter-hunted"')

    def test_stones_json_includes_stone_type(self):
        """Stones JSON should include stone_type field"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)

        # Extract stones JSON from the page
        content = response.content.decode('utf-8')
        # Find the stones-data script tag content
        import re
        match = re.search(r'<script id="stones-data" type="application/json">(.*?)</script>', content, re.DOTALL)
        self.assertIsNotNone(match, "Stones data script tag not found")

        stones_json = match.group(1).strip()
        stones = json.loads(stones_json)

        # Check that both stones are in the JSON
        stone_names = [s['PK_stone'] for s in stones]
        self.assertIn('HiddenStone', stone_names)
        self.assertIn('HuntedStone', stone_names)

        # Check that stone_type is included
        for stone in stones:
            self.assertIn('stone_type', stone)
            if stone['PK_stone'] == 'HiddenStone':
                self.assertEqual(stone['stone_type'], 'hidden')
            elif stone['PK_stone'] == 'HuntedStone':
                self.assertEqual(stone['stone_type'], 'hunted')

    def test_filter_controls_have_proper_labels(self):
        """Filter controls should have proper translated labels"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)

        # Check for filter toggle controls and labels
        self.assertContains(response, 'filter-all')
        self.assertContains(response, 'All')
        self.assertContains(response, 'Hidden')
        self.assertContains(response, 'Hunted')

    def test_map_includes_filtering_javascript(self):
        """Map page should include JavaScript for filtering"""
        response = self.client.get(reverse('stonewalker_start'))
        self.assertEqual(response.status_code, 200)

        # Check for filter-related JavaScript
        self.assertContains(response, 'applyFilters')
        self.assertContains(response, 'filterAll')
        self.assertContains(response, 'filterHidden')
        self.assertContains(response, 'filterHunted')
