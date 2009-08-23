from django.conf import settings

from template_utils.context_processors import settings_processor

pinax_settings = settings_processor(
    'CONTACT_EMAIL', 'SITE_NAME', 'STATIC_URL'
)
