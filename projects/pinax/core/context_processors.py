from django.conf import settings

def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}

def site_name(request):
    return {'site_name': getattr(settings, 'SITE_NAME', '')}
