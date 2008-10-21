from django.core.management.base import NoArgsCommand
from django.conf import settings

from avatar.models import Avatar

AUTO_GENERATE_AVATAR_SIZES = getattr(settings, 'AUTO_GENERATE_AVATAR_SIZES', (80,))

class Command(NoArgsCommand):
    help = "Import avatars from Gravatar, and store them locally."
    
    def handle_noargs(self, **options):
        for avatar in Avatar.objects.all():
            for size in AUTO_GENERATE_AVATAR_SIZES:
                print "Rebuilding Avatar id=%s at size %s." % (avatar.id, size)
                avatar.create_thumbnail(size)