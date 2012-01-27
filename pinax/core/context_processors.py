from django.conf import settings

from django.contrib.sites.models import Site


def pinax_settings(request):
    ctx = {}
    
    if Site._meta.installed:
        site = Site.objects.get_current()
        ctx.update({
            "SITE_NAME": site.name,
            "SITE_DOMAIN": site.domain
        })
    
    return ctx