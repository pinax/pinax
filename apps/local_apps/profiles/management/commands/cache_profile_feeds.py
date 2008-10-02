from django.core.management.base import NoArgsCommand
from feedutil.templatetags.feedutil import pull_feed
from account.models import OtherServiceInfo
from django.conf import settings

class Command(NoArgsCommand):
    help = 'For each blogrss url, cache the feed.'
    
    def handle_noargs(self, **options):
        for info in OtherServiceInfo.objects.filter(key="blogrss"):
            try:
                pull_feed(info.value)
            except:
                if settings.DEBUG: raise
