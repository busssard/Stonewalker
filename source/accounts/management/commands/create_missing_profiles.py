from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Create missing Profile objects for users'

    def handle(self, *args, **kwargs):
        created = 0
        for user in User.objects.all():
            Profile.objects.get_or_create(user=user)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Ensured Profile exists for {created} users.')) 