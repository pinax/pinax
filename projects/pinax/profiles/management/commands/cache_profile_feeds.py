from django.core.management.base import NoArgsCommand
from feedutil.templatetags.feedutil import pull_feed
from profiles.models import Profile
from django.conf import settings

class Command(NoArgsCommand):
    help = 'For each profile which has a blogrss url, cache the feed.'
    
    def handle_noargs(self, **options):
        for ent in Profile.objects.filter(blogrss__isnull=False).values('blogrss'):
            try:
                pull_feed(ent['blogrss'])
            except:
                if settings.DEBUG: raise
