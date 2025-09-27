#!/usr/bin/env python3
"""
Database Management Script for Production PostgreSQL
Provides CRUD operations for users and stones with easy CLI interface.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Import our database utilities
from db_utils import load_production_credentials, setup_django, test_connection

def setup():
    """Initialize database connection and Django"""
    try:
        creds = load_production_credentials()
        if setup_django():
            if test_connection():
                print("✅ Connected to production database")
                return True
            else:
                print("❌ Database connection failed")
                return False
        else:
            print("❌ Django setup failed")
            return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

# User Management Functions
def list_users(limit=50, search=None, active_only=True):
    """List users with optional filtering"""
    from django.contrib.auth.models import User
    from accounts.models import Profile, EmailAddressState
    
    users = User.objects.all()
    
    if active_only:
        users = users.filter(is_active=True)
    
    if search:
        from django.db import models
        users = users.filter(
            models.Q(username__icontains=search) |
            models.Q(email__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search)
        )
    
    users = users.order_by('-date_joined')[:limit]
    
    # If no active users found and we're filtering for active only, show a message
    if active_only and len(users) == 0:
        total_users = User.objects.count()
        inactive_users = User.objects.filter(is_active=False).count()
        print(f"\n📋 No active users found (showing 0 of {total_users} total, {inactive_users} inactive)")
        print("-" * 80)
        print("💡 Use --all flag to see inactive users: ./db list-users --all")
        return users
    
    print(f"\n📋 Users (showing {len(users)} of {User.objects.count()} total):")
    print("-" * 80)
    
    for user in users:
        try:
            profile = user.profile
            email_state = getattr(user, 'email_state', None)
            email_confirmed = email_state.is_confirmed if email_state else False
        except:
            profile = None
            email_confirmed = False
        
        status = "✅" if user.is_active else "❌"
        email_status = "✅" if email_confirmed else "⏳"
        
        print(f"{status} {user.id:4d} | {user.username:15s} | {user.email:25s} | {email_status} | {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
    
    return users

def get_user(user_id=None, username=None, email=None):
    """Get a specific user by ID, username, or email"""
    from django.contrib.auth.models import User
    
    if user_id:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            print(f"❌ User with ID {user_id} not found")
            return None
    
    if username:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"❌ User with username '{username}' not found")
            return None
    
    if email:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"❌ User with email '{email}' not found")
            return None
    
    print("❌ Please provide user_id, username, or email")
    return None

def create_user(username, email, password, first_name="", last_name=""):
    """Create a new user"""
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        print(f"✅ Created user: {user.username} (ID: {user.id})")
        return user
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return None

def update_user(user_id, **kwargs):
    """Update user information"""
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.save()
        print(f"✅ Updated user: {user.username} (ID: {user.id})")
        return user
    except User.DoesNotExist:
        print(f"❌ User with ID {user_id} not found")
        return None
    except Exception as e:
        print(f"❌ Failed to update user: {e}")
        return None

def delete_user(user_id, confirm=False):
    """Delete a user (with confirmation)"""
    from django.contrib.auth.models import User
    
    if not confirm:
        print("❌ User deletion requires confirmation. Use --confirm flag")
        return False
    
    try:
        user = User.objects.get(id=user_id)
        username = user.username
        user.delete()
        print(f"✅ Deleted user: {username} (ID: {user_id})")
        return True
    except User.DoesNotExist:
        print(f"❌ User with ID {user_id} not found")
        return False
    except Exception as e:
        print(f"❌ Failed to delete user: {e}")
        return False

def delete_inactive_old_users(confirm=False, minutes=5):
    """Delete all inactive users created more than X minutes ago"""
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    
    if not confirm:
        print("❌ Bulk deletion requires confirmation. Use --confirm flag")
        return False
    
    # Calculate cutoff time
    cutoff_time = timezone.now() - timedelta(minutes=minutes)
    
    # Find inactive users created before cutoff time
    old_inactive_users = User.objects.filter(
        is_active=False,
        date_joined__lt=cutoff_time
    )
    
    user_count = old_inactive_users.count()
    
    if user_count == 0:
        print(f"✅ No inactive users found older than {minutes} minutes")
        return True
    
    print(f"🗑️  Found {user_count} inactive users older than {minutes} minutes:")
    print("-" * 60)
    
    # Show users that will be deleted
    for user in old_inactive_users:
        age_minutes = int((timezone.now() - user.date_joined).total_seconds() / 60)
        print(f"  - {user.username} (ID: {user.id}) - created {age_minutes} minutes ago")
    
    print(f"\n⚠️  About to delete {user_count} users. This action cannot be undone!")
    
    try:
        # Delete users
        deleted_count = 0
        for user in old_inactive_users:
            username = user.username
            user_id = user.id
            user.delete()
            deleted_count += 1
            print(f"✅ Deleted user: {username} (ID: {user_id})")
        
        print(f"\n🎉 Successfully deleted {deleted_count} inactive users")
        return True
        
    except Exception as e:
        print(f"❌ Failed to delete users: {e}")
        return False

# Stone Management Functions
def list_stones(limit=50, search=None, user_id=None, stone_type=None):
    """List stones with optional filtering"""
    from main.models import Stone
    from django.contrib.auth.models import User
    from django.db import models
    
    stones = Stone.objects.all()
    
    if search:
        from django.db import models
        stones = stones.filter(
            models.Q(PK_stone__icontains=search) |
            models.Q(description__icontains=search)
        )
    
    if user_id:
        stones = stones.filter(FK_user_id=user_id)
    
    if stone_type:
        stones = stones.filter(stone_type=stone_type)
    
    stones = stones.order_by('-created_at')[:limit]
    
    print(f"\n🪨 Stones (showing {len(stones)} of {Stone.objects.count()} total):")
    print("-" * 100)
    
    for stone in stones:
        moves_count = stone.moves.count()
        distance = stone.distance_km
        
        print(f"🪨 {stone.PK_stone:10s} | {stone.FK_user.username:15s} | {stone.stone_type:6s} | {moves_count:3d} moves | {distance:6.1f}km | {stone.created_at.strftime('%Y-%m-%d %H:%M')}")
        if stone.description:
            print(f"    Description: {stone.description[:60]}{'...' if len(stone.description) > 60 else ''}")
    
    return stones

def get_stone(stone_id):
    """Get a specific stone by PK_stone"""
    from main.models import Stone
    
    try:
        return Stone.objects.get(PK_stone=stone_id)
    except Stone.DoesNotExist:
        print(f"❌ Stone with ID '{stone_id}' not found")
        return None

def create_stone(stone_id, user_id, description="", stone_type="hidden", color="#4CAF50", shape="circle"):
    """Create a new stone"""
    from main.models import Stone
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        stone = Stone.objects.create(
            PK_stone=stone_id,
            FK_user=user,
            description=description,
            stone_type=stone_type,
            color=color,
            shape=shape
        )
        print(f"✅ Created stone: {stone.PK_stone} for user {user.username}")
        return stone
    except User.DoesNotExist:
        print(f"❌ User with ID {user_id} not found")
        return None
    except Exception as e:
        print(f"❌ Failed to create stone: {e}")
        return None

def update_stone(stone_id, **kwargs):
    """Update stone information"""
    from main.models import Stone
    
    try:
        stone = Stone.objects.get(PK_stone=stone_id)
        
        for field, value in kwargs.items():
            if hasattr(stone, field):
                setattr(stone, field, value)
        
        stone.save()
        print(f"✅ Updated stone: {stone.PK_stone}")
        return stone
    except Stone.DoesNotExist:
        print(f"❌ Stone with ID '{stone_id}' not found")
        return None
    except Exception as e:
        print(f"❌ Failed to update stone: {e}")
        return None

def delete_stone(stone_id, confirm=False):
    """Delete a stone (with confirmation)"""
    from main.models import Stone
    
    if not confirm:
        print("❌ Stone deletion requires confirmation. Use --confirm flag")
        return False
    
    try:
        stone = Stone.objects.get(PK_stone=stone_id)
        stone_name = stone.PK_stone
        stone.delete()
        print(f"✅ Deleted stone: {stone_name}")
        return True
    except Stone.DoesNotExist:
        print(f"❌ Stone with ID '{stone_id}' not found")
        return False
    except Exception as e:
        print(f"❌ Failed to delete stone: {e}")
        return False

# Utility Functions
def database_stats():
    """Show database statistics"""
    from django.contrib.auth.models import User
    from main.models import Stone, StoneMove, StoneScanAttempt
    from accounts.models import Profile, EmailAddressState
    
    print("\n📊 Database Statistics:")
    print("-" * 40)
    print(f"Users: {User.objects.count()}")
    print(f"Active Users: {User.objects.filter(is_active=True).count()}")
    print(f"Profiles: {Profile.objects.count()}")
    print(f"Email States: {EmailAddressState.objects.count()}")
    print(f"Stones: {Stone.objects.count()}")
    print(f"Hidden Stones: {Stone.objects.filter(stone_type='hidden').count()}")
    print(f"Hunted Stones: {Stone.objects.filter(stone_type='hunted').count()}")
    print(f"Stone Moves: {StoneMove.objects.count()}")
    print(f"Scan Attempts: {StoneScanAttempt.objects.count()}")

def find_problematic_users():
    """Find users that might have issues"""
    from django.contrib.auth.models import User
    from accounts.models import EmailAddressState
    
    print("\n🔍 Problematic Users:")
    print("-" * 50)
    
    # Users without profiles
    users_without_profiles = User.objects.filter(profile__isnull=True)
    print(f"Users without profiles: {users_without_profiles.count()}")
    for user in users_without_profiles[:5]:
        print(f"  - {user.username} (ID: {user.id})")
    
    # Users with unconfirmed emails
    unconfirmed_emails = EmailAddressState.objects.filter(is_confirmed=False)
    print(f"\nUsers with unconfirmed emails: {unconfirmed_emails.count()}")
    for email_state in unconfirmed_emails[:5]:
        print(f"  - {email_state.user.username}: {email_state.email}")

def find_problematic_stones():
    """Find stones that might have issues"""
    from main.models import Stone, StoneMove
    
    print("\n🔍 Problematic Stones:")
    print("-" * 50)
    
    # Stones without moves
    stones_without_moves = Stone.objects.filter(moves__isnull=True)
    print(f"Stones without moves: {stones_without_moves.count()}")
    for stone in stones_without_moves[:5]:
        print(f"  - {stone.PK_stone} (User: {stone.FK_user.username})")
    
    # Stones with many moves (potential spam)
    from django.db import models
    stones_with_many_moves = Stone.objects.annotate(
        move_count=models.Count('moves')
    ).filter(move_count__gt=100)
    print(f"\nStones with >100 moves: {stones_with_many_moves.count()}")
    for stone in stones_with_many_moves[:5]:
        move_count = stone.moves.count()
        print(f"  - {stone.PK_stone}: {move_count} moves")

# CLI Interface
def show_help():
    """Show help information"""
    print("""
🗄️  Database Manager - Production PostgreSQL CRUD Operations

USAGE:
    python db_manager.py <command> [options]

USER COMMANDS:
    list-users [--limit N] [--search TEXT] [--all]     List users
    get-user --id ID | --username USER | --email EMAIL  Get specific user
    create-user --username USER --email EMAIL --password PASS  Create user
    update-user --id ID [--field VALUE]...              Update user
    delete-user --id ID --confirm                       Delete user
    delete-old-inactive --confirm [--minutes N]         Delete inactive users older than N minutes

STONE COMMANDS:
    list-stones [--limit N] [--search TEXT] [--user-id ID] [--type TYPE]  List stones
    get-stone --id STONE_ID                             Get specific stone
    create-stone --id STONE_ID --user-id USER_ID        Create stone
    update-stone --id STONE_ID [--field VALUE]...       Update stone
    delete-stone --id STONE_ID --confirm                Delete stone

UTILITY COMMANDS:
    stats                                               Show database statistics
    find-problems                                       Find problematic users/stones
    test-connection                                     Test database connection

EXAMPLES:
    python db_manager.py list-users --limit 10
    python db_manager.py get-user --username john_doe
    python db_manager.py delete-old-inactive --confirm --minutes 10
    python db_manager.py list-stones --user-id 123 --type hidden
    python db_manager.py create-stone --id STONE001 --user-id 123 --description "Test stone"
    python db_manager.py stats
    """)

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    if not setup():
        return
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # Parse arguments
    kwargs = {}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            key = args[i][2:]  # Remove '--'
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                kwargs[key] = args[i + 1]
                i += 2
            else:
                kwargs[key] = True  # Flag without value
                i += 1
        else:
            i += 1
    
    try:
        if command == "list-users":
            limit = int(kwargs.get('limit', 50))
            search = kwargs.get('search')
            all_users = 'all' in kwargs
            list_users(limit=limit, search=search, active_only=not all_users)
        
        elif command == "get-user":
            if 'id' in kwargs:
                user = get_user(user_id=int(kwargs['id']))
            elif 'username' in kwargs:
                user = get_user(username=kwargs['username'])
            elif 'email' in kwargs:
                user = get_user(email=kwargs['email'])
            else:
                print("❌ Please provide --id, --username, or --email")
                return
            
            if user:
                print(f"\n👤 User Details:")
                print(f"ID: {user.id}")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Name: {user.first_name} {user.last_name}")
                print(f"Active: {user.is_active}")
                print(f"Joined: {user.date_joined}")
        
        elif command == "create-user":
            required = ['username', 'email', 'password']
            if not all(k in kwargs for k in required):
                print("❌ Required: --username, --email, --password")
                return
            
            create_user(
                username=kwargs['username'],
                email=kwargs['email'],
                password=kwargs['password'],
                first_name=kwargs.get('first_name', ''),
                last_name=kwargs.get('last_name', '')
            )
        
        elif command == "update-user":
            if 'id' not in kwargs:
                print("❌ Required: --id")
                return
            
            user_id = int(kwargs['id'])
            update_kwargs = {k: v for k, v in kwargs.items() if k != 'id'}
            update_user(user_id, **update_kwargs)
        
        elif command == "delete-user":
            if 'id' not in kwargs or kwargs.get('confirm') != 'true':
                print("❌ Required: --id and --confirm true")
                return
            
            delete_user(int(kwargs['id']), confirm=True)
        
        elif command == "delete-old-inactive":
            if not kwargs.get('confirm'):
                print("❌ Required: --confirm flag")
                return
            
            minutes = int(kwargs.get('minutes', 5))
            delete_inactive_old_users(confirm=True, minutes=minutes)
        
        elif command == "list-stones":
            limit = int(kwargs.get('limit', 50))
            search = kwargs.get('search')
            user_id = int(kwargs['user_id']) if 'user_id' in kwargs else None
            stone_type = kwargs.get('type')
            list_stones(limit=limit, search=search, user_id=user_id, stone_type=stone_type)
        
        elif command == "get-stone":
            if 'id' not in kwargs:
                print("❌ Required: --id")
                return
            
            stone = get_stone(kwargs['id'])
            if stone:
                print(f"\n🪨 Stone Details:")
                print(f"ID: {stone.PK_stone}")
                print(f"User: {stone.FK_user.username} (ID: {stone.FK_user.id})")
                print(f"Type: {stone.stone_type}")
                print(f"Description: {stone.description}")
                print(f"Color: {stone.color}")
                print(f"Shape: {stone.shape}")
                print(f"Distance: {stone.distance_km}km")
                print(f"Created: {stone.created_at}")
                print(f"Moves: {stone.moves.count()}")
        
        elif command == "create-stone":
            required = ['id', 'user_id']
            if not all(k in kwargs for k in required):
                print("❌ Required: --id, --user_id")
                return
            
            create_stone(
                stone_id=kwargs['id'],
                user_id=int(kwargs['user_id']),
                description=kwargs.get('description', ''),
                stone_type=kwargs.get('type', 'hidden'),
                color=kwargs.get('color', '#4CAF50'),
                shape=kwargs.get('shape', 'circle')
            )
        
        elif command == "update-stone":
            if 'id' not in kwargs:
                print("❌ Required: --id")
                return
            
            stone_id = kwargs['id']
            update_kwargs = {k: v for k, v in kwargs.items() if k != 'id'}
            update_stone(stone_id, **update_kwargs)
        
        elif command == "delete-stone":
            if 'id' not in kwargs or kwargs.get('confirm') != 'true':
                print("❌ Required: --id and --confirm true")
                return
            
            delete_stone(kwargs['id'], confirm=True)
        
        elif command == "stats":
            database_stats()
        
        elif command == "find-problems":
            find_problematic_users()
            find_problematic_stones()
        
        elif command == "test-connection":
            if test_connection():
                print("✅ Database connection successful")
            else:
                print("❌ Database connection failed")
        
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
