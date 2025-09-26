#!/usr/bin/env python
"""
Script to migrate data from SQLite to PostgreSQL
"""
import os
import sys
import django

# Add the source directory to Python path
sys.path.insert(0, 'source')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import Stone
from accounts.models import Profile, Activation, EmailAddressState, EmailChangeAttempt

def migrate_data():
    print("=== Migrating data from SQLite to PostgreSQL ===")
    
    # First, get all data from SQLite (no DATABASE_URL = SQLite)
    print("1. Reading data from SQLite...")
    users = list(User.objects.all())
    stones = list(Stone.objects.all())
    profiles = list(Profile.objects.all())
    activations = list(Activation.objects.all())
    email_states = list(EmailAddressState.objects.all())
    email_changes = list(EmailChangeAttempt.objects.all())
    
    print(f"   Found: {len(users)} users, {len(stones)} stones, {len(profiles)} profiles")
    print(f"   Found: {len(activations)} activations, {len(email_states)} email states, {len(email_changes)} email changes")
    
    # Switch to PostgreSQL
    print("2. Switching to PostgreSQL...")
    os.environ['DATABASE_URL'] = 'postgresql://stone_user:stone_pass@localhost:5432/stone_dev'
    
    # Clear existing data in PostgreSQL
    print("3. Clearing existing PostgreSQL data...")
    EmailChangeAttempt.objects.all().delete()
    EmailAddressState.objects.all().delete()
    Activation.objects.all().delete()
    Profile.objects.all().delete()
    Stone.objects.all().delete()
    User.objects.all().delete()
    
    # Copy users first (they're referenced by other models)
    print("4. Copying users...")
    for user in users:
        user.pk = None  # Let Django assign new primary key
        user.save()
        print(f"   Copied user: {user.username}")
    
    # Copy stones
    print("5. Copying stones...")
    for stone in stones:
        stone.pk = None
        stone.save()
        print(f"   Copied stone: {stone.uuid}")
    
    # Copy profiles
    print("6. Copying profiles...")
    for profile in profiles:
        profile.pk = None
        profile.save()
        print(f"   Copied profile for: {profile.user.username}")
    
    # Copy activations
    print("7. Copying activations...")
    for activation in activations:
        activation.pk = None
        activation.save()
        print(f"   Copied activation: {activation.id}")
    
    # Copy email states
    print("8. Copying email states...")
    for email_state in email_states:
        email_state.pk = None
        email_state.save()
        print(f"   Copied email state: {email_state.id}")
    
    # Copy email changes
    print("9. Copying email changes...")
    for email_change in email_changes:
        email_change.pk = None
        email_change.save()
        print(f"   Copied email change: {email_change.id}")
    
    # Verify the migration
    print("10. Verifying migration...")
    print(f"   PostgreSQL now has: {User.objects.count()} users, {Stone.objects.count()} stones")
    print(f"   PostgreSQL now has: {Profile.objects.count()} profiles, {Activation.objects.count()} activations")
    
    print("=== Migration completed successfully! ===")

if __name__ == '__main__':
    migrate_data()



