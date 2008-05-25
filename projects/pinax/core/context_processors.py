from django.conf import settings

def contact_email(request):
    return {'contact_email': getattr(settings, 'CONTACT_EMAIL', '')}