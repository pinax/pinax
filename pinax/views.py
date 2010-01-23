from django.conf import settings
from django.http import HttpResponseServerError
from django.template import loader, Context



def server_error(request, template_name="500.html"):
    # You need to create a 500.html template.
    t = loader.get_template(template_name)
    ctx = Context({
        "MEDIA_URL": settings.MEDIA_URL,
        "STATIC_URL": settings.STATIC_URL,
    })
    return HttpResponseServerError(t.render(ctx))
