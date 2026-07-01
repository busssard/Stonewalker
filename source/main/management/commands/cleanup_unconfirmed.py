"""Delete stale, never-confirmed email-first (provisional) accounts.

A provisional finder account is created with an unusable password and an
unconfirmed EmailAddressState. If the finder never confirms, the account and
its held (is_confirmed=False) finds should not linger forever. This command
removes such accounts (and cascades their held finds, scan attempts, profile,
etc.) after a grace period. Standard email+password signups that are merely
pending activation are left alone (they have a usable password).
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import StoneMove


class Command(BaseCommand):
    help = 'Delete stale unconfirmed (email-first) accounts and their held finds.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=14,
                            help='Grace period in days before deletion (default 14).')
        parser.add_argument('--dry-run', action='store_true',
                            help='Report what would be deleted without deleting.')

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=options['days'])
        candidates = User.objects.filter(
            email_state__is_confirmed=False,
            date_joined__lt=cutoff,
        )
        # Only passwordless provisional accounts — never touch normal signups
        # (which have a usable password) that are merely pending activation.
        stale = [u for u in candidates if not u.has_usable_password()]

        if not stale:
            self.stdout.write('No stale unconfirmed accounts to remove.')
            return

        # Remove uploaded images for held finds before the rows cascade away.
        for user in stale:
            for move in StoneMove.objects.filter(FK_user=user):
                if move.image:
                    move.image.delete(save=False)

        if options['dry_run']:
            self.stdout.write(f'[dry-run] Would delete {len(stale)} stale unconfirmed account(s).')
            return

        ids = [u.id for u in stale]
        deleted, _ = User.objects.filter(id__in=ids).delete()
        self.stdout.write(f'Deleted {len(ids)} stale unconfirmed account(s) ({deleted} rows total).')
