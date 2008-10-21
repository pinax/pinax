from models import Avatar
from django.db.models import signals
from django.contrib.auth.models import User
from django.conf import settings

AUTO_GENERATE_AVATAR_SIZES = getattr(settings, 'AUTO_GENERATE_AVATAR_SIZES', (80,))

def update_email_hash(sender=None, instance=None, **kwargs):
    for avatar in instance.avatar_set.all():
        avatar.save()
signals.post_save.connect(update_email_hash, sender=User)

def create_default_thumbnails(instance=None, created=False, **kwargs):
    if created:
        for size in AUTO_GENERATE_AVATAR_SIZES:
            instance.create_thumbnail(size)
signals.post_save.connect(create_default_thumbnails, sender=Avatar)