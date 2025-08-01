from django.db import migrations
import uuid


def populate_uuid(apps, schema_editor):
    Stone = apps.get_model('main', 'Stone')
    for stone in Stone.objects.all():
        if not stone.uuid:
            stone.uuid = uuid.uuid4()
            stone.save()


def reverse_populate_uuid(apps, schema_editor):
    Stone = apps.get_model('main', 'Stone')
    for stone in Stone.objects.all():
        stone.uuid = None
        stone.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_stone_uuid'),
    ]

    operations = [
        migrations.RunPython(populate_uuid, reverse_populate_uuid),
    ] 