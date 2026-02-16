"""
Rename sent_off status to wandering and sent_off_at field to wandering_at.
"""

from django.db import migrations, models


def rename_sent_off_to_wandering(apps, schema_editor):
    """Data migration: update all stones with status='sent_off' to 'wandering'"""
    Stone = apps.get_model('main', 'Stone')
    Stone.objects.filter(status='sent_off').update(status='wandering')


def rename_wandering_to_sent_off(apps, schema_editor):
    """Reverse: update all stones with status='wandering' back to 'sent_off'"""
    Stone = apps.get_model('main', 'Stone')
    Stone.objects.filter(status='wandering').update(status='sent_off')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_stone_claimed_at_alter_stone_fk_user_and_more'),
    ]

    operations = [
        # 1. Update STATUS_CHOICES to include 'wandering' instead of 'sent_off'
        migrations.AlterField(
            model_name='stone',
            name='status',
            field=models.CharField(
                choices=[
                    ('unclaimed', 'Unclaimed'),
                    ('draft', 'Draft'),
                    ('published', 'Published'),
                    ('wandering', 'Wandering'),
                ],
                default='draft',
                max_length=20,
            ),
        ),
        # 2. Data migration: convert existing sent_off rows to wandering
        migrations.RunPython(
            rename_sent_off_to_wandering,
            rename_wandering_to_sent_off,
        ),
        # 3. Rename the timestamp field
        migrations.RenameField(
            model_name='stone',
            old_name='sent_off_at',
            new_name='wandering_at',
        ),
    ]
