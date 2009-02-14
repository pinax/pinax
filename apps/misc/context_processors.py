from django.conf import settings
from misc.utils import inbox_count_sources

def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}

def site_name(request):
    return {'site_name': getattr(settings, 'SITE_NAME', '')}

def combined_inbox_count(request):
    """
    A context processor that uses other context processors defined in
    setting.COMBINED_INBOX_COUNT_SOURCES to return the combined number from
    arbitrary counter sources.
    """
    count = 0
    for func in inbox_count_sources():
        counts = func(request)
        if counts:
            for value in counts.itervalues():
                try:
                    count = count + int(value)
                except (TypeError, ValueError):
                    pass
    return {'combined_inbox_count': count,}
