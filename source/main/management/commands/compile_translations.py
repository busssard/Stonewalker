"""
Django management command to compile translations.
Usage: python manage.py compile_translations
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import sys
from pathlib import Path


class Command(BaseCommand):
    help = 'Compile all translation files (.po to .mo)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force compilation even if there are warnings',
        )
        parser.add_argument(
            '--locale',
            type=str,
            help='Compile only specific locale (e.g., de, en, fr)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Compiling translations...')
        
        try:
            # Get locale directory
            locale_dir = Path(__file__).parent.parent.parent.parent / 'content' / 'locale'
            
            if not locale_dir.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Locale directory not found: {locale_dir}')
                )
                return
            
            # Check if we have any .po files
            po_files = list(locale_dir.rglob('*.po'))
            if not po_files:
                self.stdout.write(
                    self.style.WARNING('⚠️  No .po files found')
                )
                return
            
            self.stdout.write(f'📁 Found {len(po_files)} .po files')
            
            # Compile translations
            call_command('compilemessages', 
                        locale=options.get('locale'),
                        ignore=[],
                        verbosity=1)
            
            # Check if .mo files were created
            mo_files = list(locale_dir.rglob('*.mo'))
            if mo_files:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully compiled {len(mo_files)} translation files')
                )
                
                # List compiled files
                for mo_file in mo_files:
                    relative_path = mo_file.relative_to(locale_dir.parent)
                    self.stdout.write(f'   📄 {relative_path}')
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  No .mo files were created')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Translation compilation failed: {e}')
            )
            if not options.get('force'):
                sys.exit(1) 