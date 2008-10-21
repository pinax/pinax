
from announcements.models import current_announcements_for_request

def site_wide_announcements(request):
    """
    Adds the site-wide announcments to the global context of templates.
    """
    ctx = {"site_wide_announcements": current_announcements_for_request(request, site_wide=True)}
    return ctx
