"""
Tests for Sprint 2 frontend features:
- Forum external link
- Image compression enhancements
- Clickable map popups
- Dark mode
"""

import os
from django.test import TestCase
from .base import BaseAnonymousTestCase


class ForumExternalLinkTests(BaseAnonymousTestCase):
    """Test that the Forum link opens in a new tab with external URL"""

    def test_forum_link_has_target_blank(self):
        """Forum link in nav should have target='_blank'"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'target="_blank"')

    def test_forum_link_has_rel_noopener(self):
        """Forum link should have rel='noopener' for security"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'rel="noopener"')

    def test_forum_link_points_to_external_url(self):
        """Forum link should point to forum.stonewalker.org"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'href="https://forum.stonewalker.org"')

    def test_forum_link_has_external_icon(self):
        """Forum link should have an external-link SVG icon"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'external-link-icon')


class DarkModeToggleTests(BaseAnonymousTestCase):
    """Test that dark mode toggle is present in the page"""

    def test_page_has_dark_mode_toggle_button(self):
        """Page should contain the dark mode toggle button"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'id="dark-mode-toggle"')

    def test_dark_mode_toggle_has_moon_icon(self):
        """Dark mode toggle should have a moon icon"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'class="icon-moon"')

    def test_dark_mode_toggle_has_sun_icon(self):
        """Dark mode toggle should have a sun icon"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'class="icon-sun"')

    def test_dark_mode_toggle_has_aria_label(self):
        """Dark mode toggle should have an aria-label for accessibility"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'aria-label="Toggle dark mode"')


class DarkModeStylesTests(TestCase):
    """Test that CSS contains dark mode custom properties"""

    def setUp(self):
        self.css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'content', 'assets', 'css', 'styles.css'
        )
        with open(self.css_path, 'r') as f:
            self.css_content = f.read()

    def test_css_has_dark_theme_selector(self):
        """styles.css should have [data-theme='dark'] selector"""
        self.assertIn('[data-theme="dark"]', self.css_content)

    def test_css_has_bg_primary_variable(self):
        """styles.css should define --bg-primary custom property"""
        self.assertIn('--bg-primary:', self.css_content)

    def test_css_has_text_primary_variable(self):
        """styles.css should define --text-primary custom property"""
        self.assertIn('--text-primary:', self.css_content)

    def test_css_has_card_bg_variable(self):
        """styles.css should define --card-bg custom property"""
        self.assertIn('--card-bg:', self.css_content)

    def test_css_has_header_bg_variable(self):
        """styles.css should define --header-bg custom property"""
        self.assertIn('--header-bg:', self.css_content)

    def test_css_has_dark_header_override(self):
        """styles.css should have dark mode override for header"""
        self.assertIn('[data-theme="dark"] .header', self.css_content)

    def test_css_has_dark_body_override(self):
        """styles.css should have dark mode override for body"""
        self.assertIn('[data-theme="dark"] body', self.css_content)

    def test_css_has_dark_card_override(self):
        """styles.css should have dark mode override for avant-card"""
        self.assertIn('[data-theme="dark"] .avant-card', self.css_content)

    def test_css_has_dark_modal_override(self):
        """styles.css should have dark mode override for modal"""
        self.assertIn('[data-theme="dark"] .avant-modal', self.css_content)

    def test_css_has_dark_input_override(self):
        """styles.css should have dark mode override for inputs"""
        self.assertIn('[data-theme="dark"] .avant-input', self.css_content)

    def test_css_has_dark_toggle_button_style(self):
        """styles.css should have dark mode toggle button styles"""
        self.assertIn('.dark-mode-toggle', self.css_content)


class DarkModeJSTests(TestCase):
    """Test that header.js contains dark mode toggle logic"""

    def setUp(self):
        self.js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'content', 'assets', 'js', 'header.js'
        )
        with open(self.js_path, 'r') as f:
            self.js_content = f.read()

    def test_js_has_toggle_dark_mode_function(self):
        """header.js should have toggleDarkMode function"""
        self.assertIn('toggleDarkMode', self.js_content)

    def test_js_reads_local_storage_theme(self):
        """header.js should read theme from localStorage"""
        self.assertIn("localStorage.getItem('theme')", self.js_content)

    def test_js_saves_to_local_storage(self):
        """header.js should save theme to localStorage"""
        self.assertIn("localStorage.setItem('theme'", self.js_content)

    def test_js_checks_prefers_color_scheme(self):
        """header.js should check prefers-color-scheme media query"""
        self.assertIn('prefers-color-scheme: dark', self.js_content)

    def test_js_sets_data_theme_attribute(self):
        """header.js should set data-theme attribute"""
        self.assertIn("setAttribute('data-theme'", self.js_content)


class MapPopupTests(BaseAnonymousTestCase):
    """Test that map page includes popup infrastructure"""

    def test_map_page_has_popup_styles(self):
        """Stonewalker start page should reference popup CSS classes"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'sw-popup')

    def test_map_page_has_view_journey_button(self):
        """Map markers should have View Journey button in popup"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'View Journey')

    def test_map_page_has_bind_popup(self):
        """Map JS should use bindPopup for markers"""
        response = self.client.get('/stonewalker/')
        self.assertContains(response, 'bindPopup')


class ImageCompressionTests(TestCase):
    """Test that image-upload.js has compression enhancements"""

    def setUp(self):
        self.js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'content', 'assets', 'js', 'image-upload.js'
        )
        with open(self.js_path, 'r') as f:
            self.js_content = f.read()

    def test_js_has_quality_reduction_for_large_files(self):
        """image-upload.js should reduce quality for files > 1MB"""
        self.assertIn('getQuality', self.js_content)

    def test_js_has_webp_support(self):
        """image-upload.js should try WebP format"""
        self.assertIn('image/webp', self.js_content)

    def test_js_has_compression_feedback(self):
        """image-upload.js should show compression feedback"""
        self.assertIn('compressed from', self.js_content.lower())

    def test_js_has_format_size_helper(self):
        """image-upload.js should have formatSize helper"""
        self.assertIn('formatSize', self.js_content)
