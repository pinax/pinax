from django.conf import settings
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import loader, Context, RequestContext


def noop(request):
    """
    provides a callable that can be used to stub out a URL that might be
    mapped by the proxying/containing webserver.
    """
    pass


def server_error(request, template_name="500.html"):
    # You need to create a 500.html template.
    t = loader.get_template(template_name)
    ctx = Context({
        "MEDIA_URL": settings.MEDIA_URL,
        "STATIC_URL": settings.STATIC_URL,
    })
    return HttpResponseServerError(t.render(ctx))


def static_view(request, path):
    """
    serve pages directly from the templates directories.
    """
    if not path or path.endswith("/"):
        template_name = path + "index.html"
    else:
        template_name = path
    ctx = RequestContext(request)
    return render_to_response(template_name, ctx)