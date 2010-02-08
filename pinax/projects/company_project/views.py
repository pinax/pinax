from django import http
from django.conf import settings
from django.template import loader, Context
 

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(Context({
        "MEDIA_URL": settings.MEDIA_URL
    })))